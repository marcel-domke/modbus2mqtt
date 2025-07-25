let registerIndex = 0;

function createRegisterForm(register) {
  const idx = registerIndex++;
  const div = $(`
    <div class="card mt-2 p-3" data-index="${idx}">
      <label>Name:</label>
      <input class="form-control" name="name" value="${register.name || ''}">
      <label>Address:</label>
      <input class="form-control" name="address" type="text" value="${register.address || ''}">

      <label>Type:</label>
      <select class="form-control" name="type">
        <option value="uint16" ${register.type === 'uint16' ? 'selected' : ''}>Unsigned 2 Byte</option>
        <option value="int16" ${register.type === 'int16' ? 'selected' : ''}>Signed 2 Byte</option>
        <option value="uint32" ${register.type === 'uint32' ? 'selected' : ''}>Unsigned 4 Byte</option>
        <option value="int32" ${register.type === 'int32' ? 'selected' : ''}>Signed 4 Byte</option>
      </select>

      <label>Scale:</label>
      <input class="form-control" name="scale" type="number" step="0.01" value="${register.scale || 1.0}">

      <label>Interval (s):</label>
      <input class="form-control" name="interval" type="number" value="${register.interval || 60}">

      <button class="btn btn-danger mt-2" onclick="$(this).closest('.card').remove()">Remove</button>
    </div>
  `);
  $("#registerList").append(div);
}

function addRegister() {
  createRegisterForm({});
}

function loadRegisters() {
  initialRegisters.forEach(r => createRegisterForm(r));
}

function saveConfig() {
  function parseValue(value) {
    if (!isNaN(value) && value.includes(".")) {
      return parseFloat(value);
    }
    const parsedInt = parseInt(value, 10);
    if (!isNaN(parsedInt) && parsedInt.toString() === value) {
      return parsedInt;
    }
    return String(value);
  }

  const modbus = Object.fromEntries($("#modbusForm").serializeArray().map(i => [i.name, parseValue(i.value)]));

  const mqttForm = $("#mqttForm").serializeArray();
  const mqtt = {};
  mqttForm.forEach(i => mqtt[i.name] = i.value);

  const uiForm = $("#uiForm").serializeArray();
  const ui = {};
  uiForm.forEach(i => ui[i.name] = parseValue(i.value));

  const registers = [];
  $("#registerList .card").each(function () {
    const r = {};
    $(this).find("input").each(function () {
      const name = $(this).attr("name");
      let val = $(this).val();
      r[name] = parseValue(val);
    });

    const typeVal = $(this).find("select[name='type']").val();
    r['type'] = typeVal;

    registers.push(r);
  })

  const config = { modbus, mqtt, registers, ui };

  $.ajax({
    url: "/save",
    type: "POST",
    contentType: "application/json",
    data: JSON.stringify(config),
    success: () => alert("Config saved!"),
    error: () => alert("Error saving config.")
  });
}

$(document).ready(function() {
  $("#restartButton").on("click", function() {
    if (confirm("Are you sure you want to restart the modbus2mqtt service?")) {
      $.ajax({
        url: "/restart",
        type: "POST",
        //success: () => alert("Service restarted successfully!"),
        //error: () => alert("Error restarting the service."),
      });
    }
  });

  loadRegisters();
});
