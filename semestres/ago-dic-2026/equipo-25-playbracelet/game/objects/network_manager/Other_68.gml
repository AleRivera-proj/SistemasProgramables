/// @description Procesar datos de Node.js

if(!global.keyboard_debug){
	var tipo_evento = async_load[? "type"];

	// Verificamos que el evento sea de recepción de datos
	if (tipo_evento == network_type_data) {
    
	    // Extraemos el buffer (la memoria cruda que nos llegó)
	    var buffer = async_load[? "buffer"];
    
	    var json_string = buffer_read(buffer, buffer_text);
    
	    try {
	        var datos = json_parse(json_string);
			
	        if (variable_struct_exists(datos, "inclinacion")) {
	            global.giroX = datos.inclinacion;
	        }
	    } 
	    catch (e) {
	        show_debug_message("Error leyendo el JSON de Node.js: " + string(e));
	    }
		
		/*
	    // Cambiamos nuestra variable global según el mensaje recibido
	    if (mensaje == "PRESIONADO") {
	        global.boton_esp_presionado = true;
	    } 
	    else if (mensaje == "SUELTO") {
	        global.boton_esp_presionado = false;
	    }
		else if (string_char_at(mensaje, 1) == "{") {
	        try {
	            var datos_sensor = json_parse(mensaje);
            
	            // Verificamos que el JSON contenga las coordenadas del joystick
	            if (variable_struct_exists(datos_sensor, "x")) {
	                global.joystick_x = datos_sensor.x;
	                global.joystick_y = datos_sensor.y;
	            }
            
	            // Si en el futuro agregas un giroscopio, puedes detectarlo aquí
	            // if (variable_struct_exists(datos_sensor, "pitch")) { ... }
            
	        } catch(error) {
	            show_debug_message("Error leyendo JSON del sensor: " + string(error));
	        }
	    }*/
	}
}