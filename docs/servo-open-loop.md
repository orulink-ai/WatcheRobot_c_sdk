English | [简体中文](servo-open-loop_zh.md)

# Move the body safely: you cannot read the angle a servo actually reaches

For anyone writing motion controls or running the hardware check. The application
can request an angle but cannot read where the servo actually ends up. For example,
after requesting **90 degrees**, it cannot confirm that the servo reached 90 degrees,
is not stuck, or has stopped. Read this page before enabling motion.

## Before flashing or moving: clear the space

- Verify paired STM32 firmware compatibility. This SDK does not update STM32 or
  Himax firmware. Unknown compatibility or a missing complete official restore
  bundle is a **do-not-flash** blocker. Prepare [backups and official recovery](getting-started.md).
- Before **every** motion, clear the **entire possible travel**, not just the expected
  small move. Keep operator-controlled power disconnection available.
- The hardware check first commands **X90/Y120**, then **X93/Y120** or **X90/Y123**.
  The actual starting position is unknown: even a reference move can travel far
  from the other end. This is not homing, calibration or a measured three-degree
  move. The example does not automatically return to center when you exit.

## Stopping: a software report is not a physical stop

Software STOP is not an emergency-stop device; a disconnected ESP32 cannot guarantee
stop delivery. ACK means the command was received; DONE reports command completion.
Neither proves that the servo reached the angle, is not stuck, or physically stopped.
**Observe the body stop. If motion is unsafe or the stop command cannot arrive,
use operator-controlled power disconnection.** Do not wait for a software message
as proof of safety. Paired STM32 safety and an operator power cut remain necessary.

## When something goes wrong: stop operating, then investigate

1. Stop operating the controls; disconnect power manually if unsafe. Keep error
   logs and check power, connections and paired firmware.
2. Cancel pending motion. Do not keep touching to unlock controls, and **never
   replay old motion automatically**. Reconnecting, command completion or clearing
   queued events does not clear the fault or establish mechanical safety.
3. If you write recovery logic, follow the complete [body API recovery procedure](api/body.md).
   Movement afterward requires a **new user action**; a restored connection must
   not resume an old action.

## Check the physical result

A human or independent future test fixture must observe direction, the entire
range of movement and actual stop. Record paired-firmware versions, public
source/build hashes and each result. Host tests only check software state and
sequencing; historical position measurement/calibration is not a current
prerequisite or a replacement for physical observation.

Continue with the [manual hardware check](hardware-check.md).
For older context see [historical public-sync evidence](../history/SYNC_VALIDATION.md).

## Developer interface notes: compatibility does not provide angle measurements

Use this section when changing the application. Exact calls and recovery order
belong in the [body API](api/body.md).

| Result / interface | What you can conclude |
| --- | --- |
| `watcher_hw_body_request_position()` | Returns `ESP_ERR_NOT_SUPPORTED`; it cannot measure the actual angle |
| Registering a non-null position callback | Returns `ESP_ERR_NOT_SUPPORTED`; cancelling the subscription with a null callback is still safe to repeat |
| Historical `POSITION` frames or reserved identifiers | Retained for compatibility, not current measurements of actual angles |
| ACK/NACK | Command received/rejected, not proof of physical movement |
| DONE/FAULT | Command completion/fault report, not proof of actual angle, lack of stall or physical stopping |
| Requested coordinates or PWM-derived angles | Command values, not measured angles; PWM is the electrical pulse signal sent to a servo |

Command angle limits, explicit lock/release and STOP remain available. Never use
old position messages, acknowledgements or requested angles to decide that travel
is clear, limits have been recovered or the body has stopped.
