function runJarvis() {
  const button = document.querySelector('button');
  button.innerText = "🎙️ Listening...";
  button.style.backgroundColor = "#ff4081";
  button.disabled = true;

  eel.run_jarvis()().then(() => {
    button.innerText = "🎙️ Speak Command";
    button.style.backgroundColor = "#00ffe5";
    button.disabled = false;
  });
}

// Expose the chat function to be called from Python
eel.expose(showChat);

// Dynamically show chat from either 'You' or 'Jarvis'
function showChat(sender, message) {
  const chatArea = document.getElementById('chat-area');
  const formattedMessage = `<div><b>${sender}:</b> ${message}</div><br>`;
  chatArea.innerHTML += formattedMessage;
  chatArea.scrollTop = chatArea.scrollHeight;
}