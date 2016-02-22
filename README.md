# videomaton

Repositorio para proyecto Videomaton (beta)

Este videomatón consta de:
- Raspberry Pi 2 Model B con Raspbian Jessie
- Módulo de Cámara RPi
- Tarjeta de Sonido USB
- Micrófono minijack
- PiTFT 2,8" capacitiva
- USB wifi dongle
- Carcasa en 3D (modelo por corte láser o impreso en 3D)

Este videomatón está inspirado en este [GIFmatón](http://www.drumminhands.com/2014/06/15/raspberry-pi-photo-booth/) que encontré buscando información relacionada, el cual está muy bien documentado. Este GIFmatón realiza una serie de fotos, monta un GIF y después lo sube a una página de Tumblr que tengas mediante la API. El código está en Python y funciona perfectamente.

Lo que propongo con el Videomatón es lo mismo pero con un video (con audio) de 15 segundos. Los formatos aceptados por Tumblr son AAC y MP4 para audio y video, respectivamente. La medida máxima son 500px de ancho y 700px de alto. Y sólo permite 100MB de subida de video al día.

La primera tarea es conseguir sincronizar el video obtenido por el módulo de cámara con el audio obtenido por la tarjeta de sonido USB. Ya os digo que no hay mucha información al respecto, he encontrado esto:

- Picam: https://github.com/iizukanao/picam
- Corregir sincronización audio video con ffmpeg e itsoffset: https://wjwoodrow.wordpress.com/2013/02/04/correcting-for-audiovideo-sync-issues-with-the-ffmpeg-programs-itsoffset-switch/
- Hilo de Reddit: https://www.reddit.com/r/raspberry_pi/comments/3kj8q7/trying_to_sync_usb_audio_with_video_from_the/

...
