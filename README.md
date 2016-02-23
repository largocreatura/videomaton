# videomaton

Repositorio para proyecto Videomaton (beta)

Este videomatón consta de:
- Raspberry Pi 2 Model B con Raspbian Jessie
- Módulo de Cámara RPi
- Tarjeta de Sonido USB
- Micrófono minijack
- PiTFT 2,8" capacitiva
- USB wifi dongle (Para la instalación recomiendo trabajar con cable Ethernet)
- Carcasa en 3D (modelo por corte láser o impreso en 3D)

Este videomatón está inspirado en este [GIFmatón](http://www.drumminhands.com/2014/06/15/raspberry-pi-photo-booth/) que encontré buscando información relacionada, el cual está muy bien documentado. Este GIFmatón realiza una serie de fotos, monta un GIF y después lo sube a una página de Tumblr que tengas mediante la API. El código está en Python y funciona perfectamente.

Lo que propongo con el Videomatón es lo mismo pero con un video (con audio) de 15 segundos. Los formatos aceptados por Tumblr son AAC y MP4 para audio y video, respectivamente. La medida máxima son 500px de ancho y 700px de alto. Y sólo permite 100MB de subida de video al día.

La primera tarea es conseguir sincronizar el video obtenido por el módulo de cámara con el audio obtenido por la tarjeta de sonido USB. Ya os digo que no hay mucha información al respecto, he encontrado esto:

- Picam: https://github.com/iizukanao/picam
- Corregir sincronización audio video con ffmpeg e itsoffset: https://wjwoodrow.wordpress.com/2013/02/04/correcting-for-audiovideo-sync-issues-with-the-ffmpeg-programs-itsoffset-switch/
- Hilo de Reddit: https://www.reddit.com/r/raspberry_pi/comments/3kj8q7/trying_to_sync_usb_audio_with_video_from_the/

...

Vamos por partes

## 1 - Instalar Raspbian en la tarjeta SD

- [Linux](linux.md)
- [Mac OS](mac.md)
- [Windows](windows.md)

Una vez hayamos instalado Raspbian en la tarjeta, en la Raspi apagada metemos la tarjeta sd y la encendemos.


## 2 - Acceder por SSH a la RPi
https://www.raspberrypi.org/documentation/remote-access/ssh/unix.md
https://www.raspberrypi.org/documentation/remote-access/ip-address.md
Problemas de acceso con ssh: 

ssh pi@<IpAdressRaspberryPi>
password: raspberry

sudo raspi-config
- Expand File System
- Enable Camera

sudo rpi-update
sudo reboot

## 3 - Instalar FFmpeg
No hay binarios de FFmpeg para descargar ya que muchas de sus dependencias, como x264, no se pueden distribuir legalmente por lo que hay que compilarlo directamente en la Raspi. 

https://www.bitpi.co/2015/08/19/how-to-compile-ffmpeg-on-a-raspberry-pi/
libfaac: http://raspberrypi.stackexchange.com/questions/10250/how-do-i-install-libfaac-dev-on-raspi?lq=1
http://ccm.net/faq/809-debian-apt-get-no-pubkey-gpg-error

Una vez instalado hacemos una prueba de captura para ver que funciona bien

raspivid -t 10000 -w 500 -h 500 -o - | ffmpeg -i - test.mp4

Para ver si lo ha capturado bien copiamos el video de la raspi a nuestro ordenador mediante netcat y comprobamos

Ordenador que recibe: nc -lp 5000 > test.mp4
Raspi que manda: nc "IpAdress del ordenador" 5000 < test.mp4

## 3 - Audio

lsusb
enchufamos la USB sound card
lsusb
Bus 001 Device 004: ID 1b3f:2007 Generalplus Technology Inc.
arecord -l
**** List of CAPTURE Hardware Devices ****
card 1: Device [USB Audio Device], device 0: USB Audio [USB Audio]
  Subdevices: 1/1
  Subdevice #0: subdevice #0

....
