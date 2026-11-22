start-message =
    <tg-emoji emoji-id="5258011929993026890">👋</tg-emoji> <b>Hello, {$name}!</b>

    Download and convert Telegram stickers and emoji to <code>TGS</code>, <code>JSON</code>, <code>Lottie</code>, and <code>PNG</code> formats.

    <tg-emoji emoji-id="5260687681733533075">🔄</tg-emoji> <b>What I can do:</b> [/help]
    • Extract custom (premium) emoji from messages
    • Convert stickers to editable formats
    • Download entire sticker/emoji packs

    <tg-emoji emoji-id="5258330865674494479">📊</tg-emoji> <b>Total downloads:</b> {$downloads}

    <tg-emoji emoji-id="5258503720928288433">🔎</tg-emoji> <b>Quick start:</b> Send me emoji, sticker, or paste a pack link!

help-message =
    <tg-emoji emoji-id="5258503720928288433">ℹ️</tg-emoji> <b>How to use:</b>

    <tg-emoji emoji-id="5408894951440279259">1️⃣</tg-emoji> <b>Custom Emoji:</b>
    • Send any message with custom (premium) emoji
    • All emoji will be extracted and converted automatically

    <tg-emoji emoji-id="5411585799990830248">2️⃣</tg-emoji> <b>Stickers:</b>
    • Send or forward any sticker
    • Converts to editable formats (JSON, Lottie, PNG)

    <tg-emoji emoji-id="5409189019261103031">3️⃣</tg-emoji> <b>Entire Packs:</b>
    • Paste a pack link: <code>https://t.me/addstickers/PackName</code>
    • Or emoji pack: <code>https://t.me/addemoji/PackName</code>
    • The entire pack will be downloaded and converted

    <tg-emoji emoji-id="5258216851472654189">💡</tg-emoji> <b>Tip:</b> For regular static emoji, use:
    <code>https://t.me/addemoji/StaticEmoji</code>
    <code>https://t.me/addstickers/StaticEmoji</code>

    <tg-emoji emoji-id="5257969839313526622">📎</tg-emoji> <b>Output formats:</b>
    • <code>.tgs</code> — Original Telegram format
    • <code>.json</code> — Uncompressed Lottie animation
    • <code>.lottie</code> — Compressed Lottie (LottieFiles format)
    • <code>.png</code> — Raster image (first frame, 512×512px)

format-warning =
    <tg-emoji emoji-id="5258362429389152256">⚠️</tg-emoji> <b>Format Notice</b>

    Some items could not be converted.
    Original files were saved as-is.

processing = <tg-emoji emoji-id="5258514780469075716">📂</tg-emoji> <b>Processing your request...</b>

processing-pack = <tg-emoji emoji-id="5258514780469075716">📂</tg-emoji> <b>Processing: {$current}/{$total}</b>

processing-failed =
    <tg-emoji emoji-id="5258474669769497337">❌</tg-emoji> <b>Processing failed</b>

    Try again later.

pack-not-found =
    <tg-emoji emoji-id="5258474669769497337">❌</tg-emoji> <b>Pack not found</b>

    Check the link and try again.

job-in-progress = <tg-emoji emoji-id="5258474669769497337">❌</tg-emoji> Your previous request is still being processed. Please wait for it to finish.

language-select =
    🌐 <b>Language</b>

    Choose your preferred language:

language-changed = ✅ Language set to English

lang-en = English
lang-ru = Русский
