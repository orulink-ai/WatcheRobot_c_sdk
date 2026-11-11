cmake_minimum_required(VERSION 3.20)
project(watcher_body_host C)
set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)
enable_testing()
add_executable(body_test test_body.c ../../watcher_hw_body.c ../../../watcher_hw_core/watcher_hw_core.c)
target_include_directories(body_test PRIVATE include ../../include ../../../watcher_hw_core/include
  ../../../../../components/mcu_link/test_support/host/include ../../../../../components/mcu_link/include
  ../../../../../components/mcu_runtime/include ../../../../../components/mcu_motion_service/include
  ../../../../../components/mcu_led_service/include ../../../../../components/mcu_sensor_service/include
  ../../../../../components/mcu_power_service/include ../../../../../components/motion_arbiter/include)
if(MSVC)
  target_compile_options(body_test PRIVATE /W4 /UNDEBUG)
else()
  target_compile_options(body_test PRIVATE -Wall -Wextra -Werror -UNDEBUG)
endif()
add_test(NAME body_runtime COMMAND body_test)

# Compile each real example callback, not a reimplementation of its policy.
get_filename_component(examples_dir "${CMAKE_CURRENT_SOURCE_DIR}/../../../../../examples" ABSOLUTE)
# These C files include an app_main selected through a preprocessor definition.
# Keep explicit dependencies so edits rebuild both policy and startup tests on MSVC/Ninja.
set_source_files_properties(test_body.c test_example_startup.c PROPERTIES OBJECT_DEPENDS
  "${examples_dir}/body/main/app_main.c;${examples_dir}/robot/main/app_main.c")
foreach(example body robot)
  add_executable(${example}_policy_test test_body.c ../../watcher_hw_body.c ../../../watcher_hw_core/watcher_hw_core.c)
  get_target_property(host_includes body_test INCLUDE_DIRECTORIES)
  target_include_directories(${example}_policy_test PRIVATE ${host_includes}
    "${examples_dir}/common")
  target_compile_definitions(${example}_policy_test PRIVATE
    WATCHER_BODY_EXAMPLE_SOURCE="${examples_dir}/${example}/main/app_main.c")
  if(MSVC)
    target_compile_options(${example}_policy_test PRIVATE /W4 /UNDEBUG)
  else()
    target_compile_options(${example}_policy_test PRIVATE -Wall -Wextra -Werror -UNDEBUG)
  endif()
  add_test(NAME ${example}_overflow_policy COMMAND ${example}_policy_test)

  add_executable(${example}_startup_test test_example_startup.c)
  target_include_directories(${example}_startup_test PRIVATE ${host_includes} "${examples_dir}/common")
  target_compile_definitions(${example}_startup_test PRIVATE
    WATCHER_BODY_EXAMPLE_SOURCE="${examples_dir}/${example}/main/app_main.c")
  if(example STREQUAL "robot")
    target_compile_definitions(${example}_startup_test PRIVATE WATCHER_EXAMPLE_HAS_HEAD=1)
    add_test(NAME robot_startup_head_failure COMMAND ${example}_startup_test head_failure)
  endif()
  if(MSVC)
    target_compile_options(${example}_startup_test PRIVATE /W4 /WX /UNDEBUG)
  else()
    target_compile_options(${example}_startup_test PRIVATE -Wall -Wextra -Werror -UNDEBUG)
  endif()
  foreach(scenario init_failure subscribe_failure cleanup_failure success)
    add_test(NAME ${example}_startup_${scenario} COMMAND ${example}_startup_test ${scenario})
  endforeach()
endforeach()
