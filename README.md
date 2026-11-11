English | [简体中文](README_zh.md)

# WatcheRobot C SDK

WatcheRobot is an AI desktop robot for developers and creators. Use the C SDK to build
applications on the robot, combining its screen, camera, microphone, speaker, body movement
and lights into your own interactions.

## Product overview

<table>
<tr>
<td width="65%">
<p>WatcheRobot consists of a head, body and charging dock:</p>
<ul>
<li><b>Head</b>: ESP32-S3 processor, 1.45-inch touchscreen, camera, microphone, speaker and scroll wheel.</li>
<li><b>Body</b>: pan and tilt movement, body touch sensing and side lights.</li>
<li><b>Charging dock</b>: magnetic power connection and an ambient light ring.</li>
</ul>
<p>Build a screen interface, photo tool, sound interaction or touch-controlled light application, then combine these features with your own robot movements.</p>
<p>This repository provides device-side C interfaces and examples. To control existing robot firmware from a computer, use the <a href="https://github.com/orulink-ai/WatcheRobot_python_sdk">Python SDK</a>.</p>
</td>
<td width="35%" align="center">
<img src="docs/images/product/watche-robot-front.jpg" alt="Front product render of WatcheRobot" width="260" />
</td>
</tr>
</table>

## Hardware overview

| Part | Main hardware | Purpose |
| --- | --- | --- |
| Main processor | ESP32-S3, 240 MHz, 8 MB PSRAM | Runs your C application and connects the screen, audio and camera |
| Screen | 1.45-inch, 412 × 412, capacitive touch | Displays text, buttons and interfaces; accepts screen input |
| Camera | OV5647, Himax HX6538 vision processor | Takes photos and supplies a sequence of images |
| Audio | Single microphone, 1 W speaker | Records and plays sound |
| Body | CKS32F103C8T6, two SG90 servos | Provides pan and tilt movement |
| Touch and lights | Body touch sensing, side RGB lights, dock RGB light ring | Touch interaction, status indication and ambient effects |
| Connections | USB-C, head-to-body connector, magnetic dock connector | Power, development connection and head-to-body communication |

<table>
<tr>
<td align="center"><img src="docs/images/product/watche-robot-side.jpg" alt="Side product render showing the speaker and memory-card slot" width="250" /><br/>Side</td>
<td align="center"><img src="docs/images/product/watche-robot-back.jpg" alt="Rear product render showing the body power connector" width="250" /><br/>Rear</td>
</tr>
</table>

## Get started

The SDK is currently a development preview.

Follow [your first C application](docs/getting-started.md) to install ESP-IDF, build and flash the display example, then change the text on screen.

The SDK supports screen interfaces and touch, JPEG photos and streaming, PCM recording and playback, body movement, short-press touch events, lights and on-device face detection. See [hardware and firmware requirements](docs/hardware-compatibility.md) for setup, and [model installation](docs/model-deployment.md) before using face detection.

- [Feature guide](docs/features.md): find the API entry and documentation for a feature.
- [Examples](examples/README.md): choose a runnable project for display, media, lights or vision.
- [Contributing](CONTRIBUTING.md): build checks and submission guidelines for SDK changes.

## License

First-party code is [Apache-2.0](LICENSE). Third-party components and assets retain their own licenses and attribution.
