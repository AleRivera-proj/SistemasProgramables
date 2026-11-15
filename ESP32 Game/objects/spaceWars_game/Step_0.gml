if(gm_cont <= 0){
	var _rand = irandom(100);
	var _sp;
	
	if (_rand <= 50) _sp = obj_alien;
	else if(_rand <= 60) _sp = obj_alien_reverse; 
	else _sp = obj_waver;
	
	var _y = _sp == obj_alien_reverse ? room_height + 32: -32;
	instance_create_layer(irandom_range(48 + 32*6,room_width-(48 + 32*5)),_y,"Instances",_sp);
	gm_cont = sp_delay;
	sp_delay -= 3;
}else gm_cont--;