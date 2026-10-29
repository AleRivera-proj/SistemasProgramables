/// @description Mostrar estado en pantalla

draw_set_halign(fa_center);
draw_set_valign(fa_middle);

if (global.boton_esp_presionado) {
    draw_set_color(c_green);
    draw_text(100, 50, "¡ESP32 PRESIONADO!");
} else {
    draw_set_color(c_red);
    draw_text(100, 50, "Botón suelto...");
}

draw_text(100,60,global.joystick_x);