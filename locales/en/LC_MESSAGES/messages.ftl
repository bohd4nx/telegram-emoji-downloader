start-message =
    <tg-emoji emoji-id="5258011929993026890">👋</tg-emoji> <b>Hello, {$name}!</b>

    Download and convert Telegram stickers and emoji to <code>TGS</code>, <code>JSON</code>, <code>Lottie</code>, <code>PNG</code> and <code>GIF</code>.

    <tg-emoji emoji-id="5260687681733533075">🔄</tg-emoji> <b>What I can do</b>
    <blockquote>• Extract custom (premium) emoji from messages
    • Convert stickers to editable formats
    • Download entire sticker and emoji packs</blockquote>

    <tg-emoji emoji-id="5258330865674494479">📊</tg-emoji> <b>Total downloads:</b> {$downloads}

    <tg-emoji emoji-id="5258503720928288433">🔎</tg-emoji> <b>Quick start</b>
    Send an emoji or a sticker, or paste a pack link. More details: /help

help-message =
    <tg-emoji emoji-id="5258503720928288433">ℹ️</tg-emoji> <b>How to use</b>

    <tg-emoji emoji-id="5408894951440279259">1️⃣</tg-emoji> <b>Custom emoji</b>
    <blockquote>Send any message with custom (premium) emoji. All of them are extracted and converted automatically.</blockquote>

    <tg-emoji emoji-id="5411585799990830248">2️⃣</tg-emoji> <b>Stickers</b>
    <blockquote>Send or forward any sticker. Animated ones are converted to JSON, Lottie, PNG and GIF.</blockquote>

    <tg-emoji emoji-id="5409189019261103031">3️⃣</tg-emoji> <b>Packs</b>
    <blockquote>Paste a pack link and the whole pack is downloaded and converted:
    <code>https://t.me/addstickers/PackName</code>
    <code>https://t.me/addemoji/PackName</code></blockquote>

    <tg-emoji emoji-id="5258216851472654189">💡</tg-emoji> <b>Tip</b>
    <i>Regular static emoji are available as a pack:</i> <code>https://t.me/addemoji/StaticEmoji</code>

    <tg-emoji emoji-id="5257969839313526622">📎</tg-emoji> <b>Output formats</b>
    <blockquote expandable><code>.tgs</code> — original Telegram format
    <code>.json</code> — uncompressed Lottie animation
    <code>.lottie</code> — compressed Lottie (LottieFiles format)
    <code>.png</code> — first frame, 512×512 px
    <code>.gif</code> — animation, 256 px wide</blockquote>

processing = <tg-emoji emoji-id="5258514780469075716">📂</tg-emoji> <b>Processing your request…</b>

processing-pack = <tg-emoji emoji-id="5258514780469075716">📂</tg-emoji> <b>Processing:</b> {$current}/{$total}

format-warning =
    <tg-emoji emoji-id="5258362429389152256">⚠️</tg-emoji> <b>Not everything was converted</b>

    Some files could not be converted and were sent in their original format.

processing-failed =
    <tg-emoji emoji-id="5258474669769497337">❌</tg-emoji> <b>Processing failed</b>

    Please try again later.

pack-not-found =
    <tg-emoji emoji-id="5258474669769497337">❌</tg-emoji> <b>Pack not found</b>

    Check the link and try again.

job-in-progress =
    <tg-emoji emoji-id="5258514780469075716">📂</tg-emoji> <b>Request in progress</b>

    Wait for your previous request to finish, then send a new one.

language-select =
    <tg-emoji emoji-id="5260512129240276089">🌐</tg-emoji> <b>Language</b>

    Choose the interface language.

language-changed =
    ✅ <b>Language changed</b>

    The interface is now in English.

lang-en = English
lang-ru = Русский
