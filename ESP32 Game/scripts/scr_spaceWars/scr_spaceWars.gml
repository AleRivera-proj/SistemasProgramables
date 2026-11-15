function formation_1(fx,fy,fdelay,famount,finverse){
	var _fr = instance_create_layer(fx,fy,"Instances",obj_alienSpawner);
	_fr.formation = FORMATIONS.line;
	_fr.dly = fdelay;
	_fr.num = famount;
	_fr.inverse = finverse;
}

///@param {real} amount
function grant_points(amount){
	global.g2_points += amount;
	var _txt = layer_text_get_id("UIBoard","score_text");
	layer_text_text(_txt,global.g2_points);
}