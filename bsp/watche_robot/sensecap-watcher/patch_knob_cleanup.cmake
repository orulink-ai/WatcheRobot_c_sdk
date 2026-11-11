# espressif/knob 0.1.4 passes usr_data (an array address) as a GPIO on
# deletion. Patch only the known implementation; keep managed sources disposable.
file(READ "${KNOB_SOURCE}" _knob_original)
string(REPLACE "\r\n" "\n" _knob "${_knob_original}")
set(_old_gpio [=[    gpio_config(&gpio_conf);
    return ESP_OK;]=])
set(_new_gpio [=[    return gpio_config(&gpio_conf);]=])
set(_old_delete [=[    ret = _knob_gpio_deinit((int)(knob->usr_data));
    KNOB_CHECK(ESP_OK == ret, "knob deinit failed", ESP_FAIL);]=])
set(_new_delete [=[    ret = _knob_gpio_deinit((int)(intptr_t)knob->encoder_a);
    KNOB_CHECK(ESP_OK == ret, "encoder A deinit failed", ret);
    ret = _knob_gpio_deinit((int)(intptr_t)knob->encoder_b);
    KNOB_CHECK(ESP_OK == ret, "encoder B deinit failed", ret);]=])
foreach(_part gpio delete)
    string(FIND "${_knob}" "${_old_${_part}}" _old_pos)
    string(FIND "${_knob}" "${_new_${_part}}" _new_pos)
    if(_old_pos GREATER_EQUAL 0 AND _new_pos EQUAL -1)
        string(REPLACE "${_old_${_part}}" "${_new_${_part}}" _knob "${_knob}")
    elseif(NOT (_old_pos EQUAL -1 AND _new_pos GREATER_EQUAL 0))
        message(FATAL_ERROR "Unknown knob cleanup implementation in ${KNOB_SOURCE}; review dependency patch")
    endif()
endforeach()
if(NOT _knob STREQUAL _knob_original)
    file(WRITE "${KNOB_SOURCE}" "${_knob}")
endif()
