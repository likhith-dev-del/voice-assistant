// main.js

$(document).ready(function () {
    // Text animation for greeting and assistant name
    $('.text').textillate({
        loop: true,
        sync: true,
        in: { effect: "bounceIn" },
        out: { effect: "bounceOut" }
    });

    $('.siri-message').textillate({
        loop: true,
        sync: true,
        in: { effect: "fadeInUp", sync: true },
        out: { effect: "fadeOutUp", sync: true }
    });

    // SiriWave instance (only one allowed)
    let siriWaveInstance = null;

    // Helper: Show SiriWave and initialize animation if needed
    function showSiriWave() {
        $("#Oval").attr("hidden", true);
        $("#SiriWave").attr("hidden", false);

        // Create SiriWave only if not already created
        if (!siriWaveInstance) {
            siriWaveInstance = new SiriWave({
                container: document.getElementById("siri-container"),
                width: Math.min(800, $("#siri-container").width() || 800),
                height: 450,
                style: "ios9",
                amplitude: "1",
                speed: "0.1",
                autostart: true
            });
        }
    }

    // Microphone button click: play sound, show SiriWave, trigger backend
    $("#MicBtn").click(function () {
        eel.playAssistantSound();
        showSiriWave();
        eel.allCommands()();
    });

    // Keyboard shortcut: Cmd+J (Mac) or Ctrl+J (Win/Linux)
    function doc_keyUp(e) {
        if ((e.key === 'j' && (e.metaKey || e.ctrlKey))) {
            eel.playAssistantSound();
            showSiriWave();
            eel.allCommands()();
        }
    }
    document.addEventListener('keyup', doc_keyUp, false);

    // Play assistant with message (from input)
    function PlayAssistant(message) {
        if (message.trim() !== "") {
            showSiriWave();
            eel.allCommands(message);
            $("#chatbox").val("");
            $("#MicBtn").attr('hidden', false);
            $("#SendBtn").attr('hidden', true);
        }
    }

    // Toggle mic/send button based on input
    function ShowHideButton(message) {
        if (message.length === 0) {
            $("#MicBtn").attr('hidden', false);
            $("#SendBtn").attr('hidden', true);
        } else {
            $("#MicBtn").attr('hidden', true);
            $("#SendBtn").attr('hidden', false);
        }
    }

    // Input events
    $("#chatbox").keyup(function () {
        let message = $("#chatbox").val();
        ShowHideButton(message);
    });

    $("#SendBtn").click(function () {
        let message = $("#chatbox").val();
        PlayAssistant(message);
    });

    $("#chatbox").keypress(function (e) {
        if (e.which === 13) {
            let message = $("#chatbox").val();
            PlayAssistant(message);
        }
    });

    // Optionally, focus input on load for better UX
    $("#chatbox").focus();
});
