start-message =
    <tg-emoji emoji-id="5258011929993026890">👋</tg-emoji> <b>Здравствуйте, {$name}!</b>

    Скачивайте и конвертируйте стикеры и эмодзи Telegram в форматы <code>TGS</code>, <code>JSON</code>, <code>Lottie</code>, <code>PNG</code> и <code>GIF</code>.

    <tg-emoji emoji-id="5260687681733533075">🔄</tg-emoji> <b>Что я умею</b>
    <blockquote>• Извлекаю кастомные (премиум) эмодзи из сообщений
    • Конвертирую стикеры в редактируемые форматы
    • Скачиваю целые паки стикеров и эмодзи</blockquote>

    <tg-emoji emoji-id="5258330865674494479">📊</tg-emoji> <b>Всего скачиваний:</b> {$downloads}

    <tg-emoji emoji-id="5258503720928288433">🔎</tg-emoji> <b>Быстрый старт</b>
    Отправьте эмодзи или стикер либо вставьте ссылку на пак. Подробности: /help

help-message =
    <tg-emoji emoji-id="5258503720928288433">ℹ️</tg-emoji> <b>Как пользоваться</b>

    <tg-emoji emoji-id="5408894951440279259">1️⃣</tg-emoji> <b>Кастомные эмодзи</b>
    <blockquote>Отправьте любое сообщение с кастомными (премиум) эмодзи. Все они будут извлечены и конвертированы автоматически.</blockquote>

    <tg-emoji emoji-id="5411585799990830248">2️⃣</tg-emoji> <b>Стикеры</b>
    <blockquote>Отправьте или перешлите любой стикер. Анимированные будут конвертированы в JSON, Lottie, PNG и GIF.</blockquote>

    <tg-emoji emoji-id="5409189019261103031">3️⃣</tg-emoji> <b>Паки</b>
    <blockquote>Вставьте ссылку на пак, и весь пак будет скачан и конвертирован:
    <code>https://t.me/addstickers/PackName</code>
    <code>https://t.me/addemoji/PackName</code></blockquote>

    <tg-emoji emoji-id="5258216851472654189">💡</tg-emoji> <b>Подсказка</b>
    <i>Обычные статические эмодзи доступны как пак:</i> <code>https://t.me/addemoji/StaticEmoji</code>

    <tg-emoji emoji-id="5257969839313526622">📎</tg-emoji> <b>Форматы вывода</b>
    <blockquote expandable><code>.tgs</code> — оригинальный формат Telegram
    <code>.json</code> — несжатая Lottie-анимация
    <code>.lottie</code> — сжатый Lottie (формат LottieFiles)
    <code>.png</code> — первый кадр, 512×512 px
    <code>.gif</code> — анимация, 256 px по ширине</blockquote>

processing = <tg-emoji emoji-id="5258514780469075716">📂</tg-emoji> <b>Обрабатываю ваш запрос…</b>

processing-pack = <tg-emoji emoji-id="5258514780469075716">📂</tg-emoji> <b>Обрабатываю:</b> {$current}/{$total}

format-warning =
    <tg-emoji emoji-id="5258362429389152256">⚠️</tg-emoji> <b>Конвертировано не всё</b>

    Некоторые файлы не удалось конвертировать, они отправлены в исходном формате.

processing-failed =
    <tg-emoji emoji-id="5258474669769497337">❌</tg-emoji> <b>Не удалось обработать запрос</b>

    Пожалуйста, попробуйте позже.

pack-not-found =
    <tg-emoji emoji-id="5258474669769497337">❌</tg-emoji> <b>Пак не найден</b>

    Проверьте ссылку и попробуйте ещё раз.

job-in-progress =
    <tg-emoji emoji-id="5258514780469075716">📂</tg-emoji> <b>Запрос обрабатывается</b>

    Дождитесь завершения предыдущего запроса и отправьте новый.

language-select =
    <tg-emoji emoji-id="5260512129240276089">🌐</tg-emoji> <b>Язык</b>

    Выберите язык интерфейса.

language-changed =
    ✅ <b>Язык изменён</b>

    Теперь интерфейс на русском языке.

lang-en = English
lang-ru = Русский
