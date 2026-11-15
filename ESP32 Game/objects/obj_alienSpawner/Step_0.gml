switch(formation){
	case FORMATIONS.line:
		if(cnt1 < num){
			if(cnt2 <= 0){
				var _sp = inverse ? obj_alien_reverse : obj_alien;
				instance_create_layer(x,y,"Instances",_sp);
				cnt2 = dly;
				cnt1++;
			}else cnt2--;
		}else instance_destroy();
		break;
	default:
		instance_destroy();
}