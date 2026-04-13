    const audio = document.getElementById('bg-music');
    const btn = document.getElementById('play-pause');

    document.addEventListener('DOMContentLoaded', () => {
      audio.volume = 0.5;
    });

    btn.addEventListener('click', () => {
      if (audio.paused) {
        audio.play();
        btn.textContent = '🔇 Pause';
      } else {
        audio.pause();
        btn.textContent = '🎵 Play';
      }
    });
