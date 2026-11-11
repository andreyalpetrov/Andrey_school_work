// Чат. История диалога хранится только в переменной history,
// поэтому после перезагрузки страницы разговор начинается заново.

(function () {
    const thread = document.getElementById('thread');
    const scroller = document.getElementById('messages');
    const form = document.getElementById('chat-form');
    const input = document.getElementById('prompt');
    const sendButton = document.getElementById('send');
    const newChatButton = document.getElementById('new-chat');
    const emptyHtml = document.getElementById('empty').outerHTML;

    let history = [];        // [{role: 'user' | 'assistant', content: '...'}]
    let controller = null;   // AbortController текущего запроса (null, если модель не отвечает)
    let dialogId = 0;        // увеличивается при нажатии "Новый диалог"

    // ------------------------------------------------------------------
    // Простая разметка Markdown: модель часто пишет **жирным**, списками и кодом.
    // Текст сначала экранируется, поэтому HTML из ответа модели не выполняется.
    // ------------------------------------------------------------------

    function escapeHtml(text) {
        return text.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
    }

    function inline(text) {
        // Нечётные части после деления по ` - это код, в нём разметку не трогаем
        return text.split('`').map(function (part, i) {
            if (i % 2 === 1) return '<code>' + part + '</code>';
            return part
                .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
                .replace(/(^|[\s(])\*([^*\s][^*]*)\*/g, '$1<em>$2</em>');
        }).join('');
    }

    function renderText(text) {
        const lines = escapeHtml(text).split('\n');
        let html = '';
        let paragraph = [];
        let list = null;   // 'ul' | 'ol' | null

        function closeParagraph() {
            if (paragraph.length) { html += '<p>' + paragraph.join('<br>') + '</p>'; paragraph = []; }
        }
        function closeList() {
            if (list) { html += '</' + list + '>'; list = null; }
        }

        lines.forEach(function (line) {
            let m;
            if (!line.trim()) {
                closeParagraph(); closeList();
            } else if ((m = line.match(/^\s*(#{1,4})\s+(.*)$/))) {
                closeParagraph(); closeList();
                const level = Math.min(m[1].length + 2, 5);
                html += '<h' + level + '>' + inline(m[2]) + '</h' + level + '>';
            } else if ((m = line.match(/^\s*[-*•]\s+(.*)$/))) {
                closeParagraph();
                if (list !== 'ul') { closeList(); html += '<ul>'; list = 'ul'; }
                html += '<li>' + inline(m[1]) + '</li>';
            } else if ((m = line.match(/^\s*\d+[.)]\s+(.*)$/))) {
                closeParagraph();
                if (list !== 'ol') { closeList(); html += '<ol>'; list = 'ol'; }
                html += '<li>' + inline(m[1]) + '</li>';
            } else if (/^\s*(-{3,}|\*{3,})\s*$/.test(line)) {
                closeParagraph(); closeList();
                html += '<hr>';
            } else {
                closeList();
                paragraph.push(inline(line));
            }
        });
        closeParagraph(); closeList();
        return html;
    }

    function renderMarkdown(source) {
        // Нечётные части после деления по ``` - блоки кода
        return source.split('```').map(function (part, i) {
            if (i % 2 === 0) return renderText(part);
            const code = part.replace(/^[^\n]*\n?/, '');   // первая строка - название языка
            return '<pre><code>' + escapeHtml(code.replace(/\n$/, '')) + '</code></pre>';
        }).join('');
    }

    // ------------------------------------------------------------------
    // Отрисовка сообщений
    // ------------------------------------------------------------------

    function nearBottom() {
        return scroller.scrollHeight - scroller.scrollTop - scroller.clientHeight < 80;
    }

    function scrollDown() {
        scroller.scrollTop = scroller.scrollHeight;
    }

    function addUserMessage(text) {
        const el = document.createElement('div');
        el.className = 'msg msg-user';
        el.textContent = text;
        thread.appendChild(el);
        return el;
    }

    function addAssistantMessage() {
        const el = document.createElement('div');
        el.className = 'msg msg-assistant';
        el.innerHTML =
            '<details class="thinking" hidden>' +
            '<summary><span class="thinking-label">Размышляет</span> <span class="thinking-time"></span></summary>' +
            '<div class="thinking-text"></div>' +
            '</details>' +
            '<div class="answer"><span class="waiting">Модель думает…</span></div>';
        thread.appendChild(el);
        return {
            root: el,
            details: el.querySelector('.thinking'),
            label: el.querySelector('.thinking-label'),
            time: el.querySelector('.thinking-time'),
            thinking: el.querySelector('.thinking-text'),
            answer: el.querySelector('.answer')
        };
    }

    function addNote(parent, text, isError) {
        const note = document.createElement('p');
        note.className = isError ? 'note note-error' : 'note';
        note.textContent = text;
        parent.appendChild(note);
    }

    function setBusy(busy) {
        sendButton.textContent = busy ? 'Стоп' : 'Отправить';
        sendButton.classList.toggle('stop', busy);
    }

    // ------------------------------------------------------------------
    // Отправка сообщения и чтение потока
    // ------------------------------------------------------------------

    async function ask(text) {
        const empty = document.getElementById('empty');
        if (empty) empty.remove();

        const myDialog = dialogId;
        const userEl = addUserMessage(text);
        history.push({ role: 'user', content: text });
        const view = addAssistantMessage();
        scrollDown();

        let thinkingText = '';
        let answerText = '';
        let errorText = '';
        let thinkingStarted = 0;
        let thinkingTimer = null;
        let redrawPlanned = false;

        function stopThinkingTimer() {
            if (!thinkingTimer) return;
            clearInterval(thinkingTimer);
            thinkingTimer = null;
            const seconds = Math.max(1, Math.round((Date.now() - thinkingStarted) / 1000));
            view.label.textContent = 'Размышлял';
            view.time.textContent = seconds + ' с';
        }

        function redraw() {
            redrawPlanned = false;
            const stick = nearBottom();
            if (thinkingText) {
                view.thinking.textContent = thinkingText;
                if (!answerText) view.thinking.scrollTop = view.thinking.scrollHeight;
            }
            if (answerText) view.answer.innerHTML = renderMarkdown(answerText);
            if (stick) scrollDown();
        }

        function planRedraw() {
            if (!redrawPlanned) { redrawPlanned = true; requestAnimationFrame(redraw); }
        }

        function handle(ev) {
            if (ev.type === 'thinking') {
                if (!thinkingStarted) {
                    thinkingStarted = Date.now();
                    view.details.hidden = false;
                    view.details.open = true;
                    view.answer.innerHTML = '';
                    thinkingTimer = setInterval(function () {
                        view.time.textContent = Math.round((Date.now() - thinkingStarted) / 1000) + ' с';
                    }, 1000);
                }
                thinkingText += ev.text;
                planRedraw();
            } else if (ev.type === 'content') {
                if (!answerText) {
                    // Начался ответ: рассуждения сворачиваем, их можно раскрыть щелчком
                    stopThinkingTimer();
                    view.details.open = false;
                }
                answerText += ev.text;
                planRedraw();
            } else if (ev.type === 'error') {
                errorText = ev.text;
            }
        }

        controller = new AbortController();
        setBusy(true);
        let stopped = false;

        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ messages: history }),
                signal: controller.signal
            });

            if (response.status === 401) {
                window.location.href = '/login';
                return;
            }
            if (!response.ok) {
                const data = await response.json().catch(function () { return {}; });
                errorText = data.error || 'Сервер вернул ошибку ' + response.status + '.';
            } else {
                // Сервер присылает по одной JSON-строке на каждый кусочек текста
                const reader = response.body.getReader();
                const decoder = new TextDecoder();
                let buffer = '';
                while (true) {
                    const part = await reader.read();
                    if (part.done) break;
                    buffer += decoder.decode(part.value, { stream: true });
                    const lines = buffer.split('\n');
                    buffer = lines.pop();
                    lines.forEach(function (line) {
                        if (line.trim()) handle(JSON.parse(line));
                    });
                }
            }
        } catch (e) {
            if (e.name === 'AbortError') stopped = true;
            else errorText = 'Соединение с сервером прервалось.';
        }

        stopThinkingTimer();
        controller = null;
        setBusy(false);
        if (myDialog !== dialogId) return;   // пока шёл ответ, нажали "Новый диалог"
        redraw();

        answerText = answerText.trim();
        if (answerText) {
            history.push({ role: 'assistant', content: answerText });
        } else {
            // Ответа нет - убираем вопрос из истории, чтобы модель не увидела его дважды
            history.pop();
            userEl.classList.add('msg-dropped');
            view.answer.innerHTML = '';
        }

        if (errorText) addNote(view.root, errorText, true);
        else if (stopped) addNote(view.root, answerText ? 'Ответ остановлен.' : 'Запрос остановлен, модель его не запомнила.');
        else if (!answerText) addNote(view.root, 'Модель не прислала ответ. Попробуйте ещё раз.', true);

        if (nearBottom()) scrollDown();
        input.focus();
    }

    // ------------------------------------------------------------------
    // Обработчики
    // ------------------------------------------------------------------

    function resizeInput() {
        input.style.height = 'auto';
        input.style.height = Math.min(input.scrollHeight, 200) + 'px';
    }

    form.addEventListener('submit', function (e) {
        e.preventDefault();
        if (controller) {          // модель отвечает - кнопка работает как "Стоп"
            controller.abort();
            return;
        }
        const text = input.value.trim();
        if (!text) return;
        input.value = '';
        resizeInput();
        ask(text);
    });

    input.addEventListener('input', resizeInput);

    input.addEventListener('keydown', function (e) {
        if (e.key === 'Enter' && !e.shiftKey && !e.isComposing) {
            e.preventDefault();
            if (!controller) form.requestSubmit();
        }
    });

    newChatButton.addEventListener('click', function () {
        if (controller) controller.abort();
        dialogId += 1;
        history = [];
        thread.innerHTML = emptyHtml;
        input.focus();
    });

    // Для автоматической проверки разметки (в браузере не используется)
    if (typeof module !== 'undefined') module.exports = { renderMarkdown: renderMarkdown };
})();
