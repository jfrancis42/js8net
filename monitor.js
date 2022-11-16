// This function takes in latitude and longitude of two location and
// returns the distance between them as the crow flies (in
// km). (Converted to miles - n0gq)
// https://stackoverflow.com/questions/18883601/function-to-calculate-distance-between-two-coordinates
function calcCrow(lat1, lon1, lat2, lon2) {
    var R=6371; // km
    var dLat=toRadians(lat2-lat1);
    var dLon=toRadians(lon2-lon1);
    var lat1=toRadians(lat1);
    var lat2=toRadians(lat2);

    var a=Math.sin(dLat/2) * Math.sin(dLat/2) +
	Math.sin(dLon/2) * Math.sin(dLon/2) * Math.cos(lat1) * Math.cos(lat2);
    var c=2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
    var d=R * c;
    return d*0.6214;
}

// Converts from degrees to radians.
function toRadians(degrees) {
  return degrees * Math.PI / 180;
};

// Converts from radians to degrees.
function toDegrees(radians) {
    return radians * 180 / Math.PI;
}

// https://stackoverflow.com/questions/46590154/calculate-bearing-between-2-points-with-javascript
function bearing(lat1, lon1, lat2, lon2){
    lat1=toRadians(lat1);
    lon1=toRadians(lon1);
    lat2=toRadians(lat2);
    lon2=toRadians(lon2);

    y=Math.sin(lon2 - lon1) * Math.cos(lat2);
    x=Math.cos(lat1) * Math.sin(lat2) -
	Math.sin(lat1) * Math.cos(lat2) * Math.cos(lon2 - lon1);
    brng=Math.atan2(y, x);
    brng=toDegrees(brng);
    return (brng + 360) % 360;
}

// Convert the speed integer into an english speed.
function english_speed(s) {
    if(s==0) {
	return('Normal');
    } else if(s==1) {
	return('Fast');
    } else if(s==2) {
	return('Turbo');
    } else if(s==4) {
	return('Slow');
    } else {
	return('Invalid');
    }
}

// https://stackoverflow.com/questions/4967223/delete-a-row-from-a-table-by-id
function removeRow(id) {
    var tr = document.getElementById(id);
    if (tr) {
	if (tr.nodeName == 'TR') {
	    var tbl = tr; // Look up the hierarchy for TABLE
	    while (tbl != document && tbl.nodeName != 'TABLE') {
		tbl = tbl.parentNode;
	    }
	    
	    if (tbl && tbl.nodeName == 'TABLE') {
		while (tr.hasChildNodes()) {
		    tr.removeChild( tr.lastChild );
		}
		tr.parentNode.removeChild( tr );
	    }
	} else {
	    alert( 'Specified document element is not a TR. id=' + id );
	}
    } else {
	alert( 'Specified document element is not found. id=' + id );
    }
}

var first_time=true;

// Build the table contents page.
var intervalId=setInterval(async function() {
    // age
    now=Math.floor(Date.now()/1000)

    if(first_time) {
	// Get the color JSON.
	console.log('Fetching /colors');
	var color_response=await fetch('/colors');
	var color_stuff=await color_response.text();
	
	// Convert the text into JSON. todo: shouldn't have to do this.
	colors=JSON.parse(color_stuff);
	
	// Get the friends JSON.
	console.log('Fetching /friends');
	var friend_response=await fetch('/friends');
	var friend_stuff=await friend_response.text();
	
	// Convert the text into JSON. todo: shouldn't have to do this.
	friends=JSON.parse(friend_stuff);
	
	// Get the station JSON.
	console.log('Fetching /stations');
	var station_response=await fetch('/stations');
	var station_stuff=await station_response.text();
	
	// Convert the text into JSON. todo: shouldn't have to do this.
	stations=JSON.parse(station_stuff);
    } else if(now%5==0) {
	// Get the station JSON.
	console.log('Fetching /stations');
	var station_response=await fetch('/stations');
	var station_stuff=await station_response.text();
	
	// Convert the text into JSON. todo: shouldn't have to do this.
	stations=JSON.parse(station_stuff);
    }
    
    if(now%30==0) {
	console.log('Fetching connections image');
	document.getElementById("c-img").src='/connections/'+now+'.jpg';
    }

    if(first_time) {
	// Find the 'stations' table.
	var table=document.getElementById('stations');
	
	// Create the table headers.
	var thead=document.createElement('thead');
	table.appendChild(thead);
	
	thead.appendChild(document.createElement('th')).
	    appendChild(document.createTextNode('Call'));
	thead.appendChild(document.createElement('th')).
	    appendChild(document.createTextNode('Grid'));
	thead.appendChild(document.createElement('th')).
	    appendChild(document.createTextNode('Host'));
	thead.appendChild(document.createElement('th')).
	    appendChild(document.createTextNode('Port'));
	thead.appendChild(document.createElement('th')).
	    appendChild(document.createTextNode('Speed'));
	thead.appendChild(document.createElement('th')).
	    appendChild(document.createTextNode('Dial'));
	thead.appendChild(document.createElement('th')).
	    appendChild(document.createTextNode('Carrier'));
	thead.appendChild(document.createElement('th')).
	    appendChild(document.createTextNode('Radio'));
    }
    
    var table=document.getElementById('stations');
    
    // Insert the radio info.
    for (var key in stations) {
	if (stations.hasOwnProperty(key)) {
	    var row=document.getElementById(key);
	    var age=Math.round(now-stations[key].time);
	    // todo: this shouldn't be a fixed time
	    if(age<=3600) {
		var new_row=false;
		if(!row) {
		    row=table.insertRow(0);
		    row.id=key;
		    new_row=true;
		}
		if(new_row) {
		    var cell=row.insertCell(-1);
		    cell.innerHTML=stations[key]['call'];
		} else {
		    row.cells[0].innerHTML=stations[key]['call'];
		}
		if(new_row) {
		    var cell=row.insertCell(-1);
		    cell.innerHTML=stations[key]['grid'];
		} else {
		    row.cells[1].innerHTML=stations[key]['grid'];
		}
		if(new_row) {
		    var cell=row.insertCell(-1);
		    cell.innerHTML=stations[key]['host'];
		} else {
		    row.cells[2].innerHTML=stations[key]['host'];
		}
		if(new_row) {
		    var cell=row.insertCell(-1);
		    cell.innerHTML=stations[key]['port'];
		} else {
		    row.cells[3].innerHTML=stations[key]['port'];
		}
		if(new_row) {
		    var cell=row.insertCell(-1);
		    cell.innerHTML=english_speed(stations[key]['speed']);
		} else {
		    row.cells[4].innerHTML=english_speed(stations[key]['speed']);
		}
		if(new_row) {
		    var cell=row.insertCell(-1);
		    cell.innerHTML=stations[key]['dial']/1000.0;
		} else {
		    row.cells[5].innerHTML=stations[key]['dial']/1000.0;
		}
		if(new_row) {
		    var cell=row.insertCell(-1);
		    cell.innerHTML=stations[key]['carrier'];
		} else {
		    row.cells[6].innerHTML=stations[key]['carrier'];
		}
		if(new_row) {
		    var cell=row.insertCell(-1);
		    cell.innerHTML=stations[key]['radio'];
		} else {
		    row.cells[7].innerHTML=stations[key]['radio'];
		}
	    } else {
		if(row) {
		    removeRow(key);
		}
	    }
	}
    }
    
    if(first_time) {
	// Get the traffic JSON.
	console.log('Fetching /traffic');
	var traffic_response=await fetch('/traffic');
	var traffic_stuff=await traffic_response.text();
	
	// Convert the text into JSON. todo: shouldn't have to do this.
	traffic=JSON.parse(traffic_stuff);
    } else if(now%5==0) {
	// Get the traffic JSON.
	console.log('Fetching /traffic');
	var traffic_response=await fetch('/traffic');
	var traffic_stuff=await traffic_response.text();
	
	// Convert the text into JSON. todo: shouldn't have to do this.
	traffic=JSON.parse(traffic_stuff);
    }

    // Find the 'traffic' table.
    var table=document.getElementById('traffic');

    if(first_time) {
	// Create the traffic headers.
	var thead=document.createElement('thead');
	table.appendChild(thead);
	thead.appendChild(document.createElement("th")).
	    appendChild(document.createTextNode('Radio'));
	thead.appendChild(document.createElement("th")).
	    appendChild(document.createTextNode('From'));
	thead.appendChild(document.createElement("th")).
	    appendChild(document.createTextNode('To'));
	thead.appendChild(document.createElement("th")).
	    appendChild(document.createTextNode('Grid'));
	thead.appendChild(document.createElement("th")).
	    appendChild(document.createTextNode('Dist'));
	thead.appendChild(document.createElement("th")).
	    appendChild(document.createTextNode('Age'));
	thead.appendChild(document.createElement("th")).
	    appendChild(document.createTextNode('SNR'));
	thead.appendChild(document.createElement("th")).
	    appendChild(document.createTextNode('Speed'));
	thead.appendChild(document.createElement("th")).
	    appendChild(document.createTextNode('Frequency'));
	thead.appendChild(document.createElement("th")).
	    appendChild(document.createTextNode('Received Text'));
    }
    
    // Insert the traffic rows.
    var l=traffic.length;
    for(let i=0; i<l; i++) {
	let rx=traffic[i];
	if(rx.type=='RX.DIRECTED') {
	    var row=document.getElementById(rx.id);
	    var new_row=false
	    if(!row) {
		row=table.insertRow(0);
		if(rx.id) {
		    row.id=rx.id;
		}	
		new_row=true
	    }
	    
	    // radio
	    if(new_row) {
		var cell=row.insertCell(-1);
		cell.innerHTML=stations[rx.uuid]['call']+':'+stations[rx.uuid]['radio'];
	    }
	    
            // from
	    if(new_row) {
		var cell=row.insertCell(-1);
		var f=false;
		if(rx.from_call in friends) {
		    f=friends[rx.from_call]
		}
		if(f && f[0]!='') {
		    cell.innerHTML='<img src="/flags/'+rx.from_flag+'" alt="" width="24" height="24" />&nbsp;&nbsp;<a href="https://pskreporter.info/pskmap.html?preset&callsign='+rx.from_call+'&timerange=1800&hideunrec=1&blankifnone=1&hidepink=1&showsnr=1&showlines=1&mapCenter=39.09371454584385,-97.249548593876,5.3519901583255205" target="_blank">'+rx.from_call+'</a>'+': '+f[0];
		} else if(rx.from_info) {
		    cell.innerHTML='<img src="/flags/'+rx.from_flag+'" alt="" width="24" height="24" />&nbsp;&nbsp;<a href="https://pskreporter.info/pskmap.html?preset&callsign='+rx.from_call+'&timerange=1800&hideunrec=1&blankifnone=1&hidepink=1&showsnr=1&showlines=1&mapCenter=39.09371454584385,-97.249548593876,5.3519901583255205" target="_blank">'+rx.from_call+'</a>'+': '+rx.from_info;
		} else if(rx.from_country) {
		    cell.innerHTML='<img src="/flags/'+rx.from_flag+'" alt="" width="24" height="24" />&nbsp;&nbsp;<a href="https://pskreporter.info/pskmap.html?preset&callsign='+rx.from_call+'&timerange=1800&hideunrec=1&blankifnone=1&hidepink=1&showsnr=1&showlines=1&mapCenter=39.09371454584385,-97.249548593876,5.3519901583255205" target="_blank">'+rx.from_call+'</a>'+': '+rx.from_country;
		} else {
		    cell.innerHTML='<img src="/flags/'+rx.from_flag+'" alt="" width="24" height="24" />&nbsp;&nbsp;<a href="https://pskreporter.info/pskmap.html?preset&callsign='+rx.from_call+'&timerange=1800&hideunrec=1&blankifnone=1&hidepink=1&showsnr=1&showlines=1&mapCenter=39.09371454584385,-97.249548593876,5.3519901583255205" target="_blank">'+rx.from_call+'</a>';
		}
		if(f) {
		    if(f[1]!='') {
			cell.style.backgroundColor=f[1];
		    } else {
			cell.style.backgroundColor=colors.friend;
		    }
		}
	    }
	    
            // to
	    if(new_row) {
		var cell=row.insertCell(-1);
		var f=false;
		if(rx.to_call in friends) {
		    f=friends[rx.to_call]
		}
		if(rx.to_at) {
		    cell.innerHTML=rx.to_call;
		    cell.style.backgroundColor=colors.at;
		} else {
		    if(f && f[0]!='') {
			cell.innerHTML='<img src="/flags/'+rx.to_flag+'" alt="" width="24" height="24" />&nbsp;&nbsp;<a href="https://pskreporter.info/pskmap.html?preset&callsign='+rx.to_call+'&timerange=1800&hideunrec=1&blankifnone=1&hidepink=1&showsnr=1&showlines=1&mapCenter=39.09371454584385,-97.249548593876,5.3519901583255205" target="_blank">'+rx.to_call+'</a>'+': '+f[0];
		    } else if(rx.to_info) {
			cell.innerHTML='<img src="/flags/'+rx.to_flag+'" alt="" width="24" height="24" />&nbsp;&nbsp;<a href="https://pskreporter.info/pskmap.html?preset&callsign='+rx.to_call+'&timerange=1800&hideunrec=1&blankifnone=1&hidepink=1&showsnr=1&showlines=1&mapCenter=39.09371454584385,-97.249548593876,5.3519901583255205" target="_blank">'+rx.to_call+'</a>'+': '+rx.to_info;
		    } else if(rx.to_country) {
			cell.innerHTML='<img src="/flags/'+rx.to_flag+'" alt="" width="24" height="24" />&nbsp;&nbsp;<a href="https://pskreporter.info/pskmap.html?preset&callsign='+rx.to_call+'&timerange=1800&hideunrec=1&blankifnone=1&hidepink=1&showsnr=1&showlines=1&mapCenter=39.09371454584385,-97.249548593876,5.3519901583255205" target="_blank">'+rx.to_call+'</a>'+': '+rx.to_country;
		    } else {
			cell.innerHTML='<img src="/flags/'+rx.to_flag+'" alt="" width="24" height="24" />&nbsp;&nbsp;<a href="https://pskreporter.info/pskmap.html?preset&callsign='+rx.to_call+'&timerange=1800&hideunrec=1&blankifnone=1&hidepink=1&showsnr=1&showlines=1&mapCenter=39.09371454584385,-97.249548593876,5.3519901583255205" target="_blank">'+rx.to_call+'</a>';
		    }
		    if(f) {
			if(f[1]!='') {
			    cell.style.backgroundColor=f[1];
			} else {
			    cell.style.backgroundColor=colors.friend;
			}
		    }
		}
	    }
	    
            // grid
	    if(new_row) {
		var cell=row.insertCell(-1);
		if(rx.grid) {
		    cell.innerHTML=rx.grid;
		}
	    }
	    
	    // distance
	    if(new_row) {
		var cell=row.insertCell(-1);
		if(rx.lat && rx.lon && stations[rx.uuid]['lat'] && stations[rx.uuid]['lon']) {
		    var dist=Math.round(calcCrow(stations[rx.uuid]['lat'],stations[rx.uuid]['lon'],
						 rx.lat,rx.lon));
		    var brg=Math.round(bearing(stations[rx.uuid]['lat'],stations[rx.uuid]['lon'],
						   rx.lat,rx.lon));
		    cell.innerHTML=dist+' mi @ '+brg+' deg';
		    // Highlight anyone within 150 mi. todo: Should
		    // probably make this an adjustable parameter.
		    if(dist<=150) {
			cell.style.backgroundColor=colors.close;
		    }
		}
	    }
	    
	    // age todo: fix timezone issue. collector is stamping in local time, not UTC
	    if(new_row) {
		var cell=row.insertCell(-1);
		cell.innerHTML=new Date(Math.round(now-rx.time)*1000).toISOString().substr(11, 8);
	    } else {
		row.cells[5].innerHTML=new Date(Math.round(now-rx.time)*1000).toISOString().substr(11, 8);
	    }
	    
	    // SNR
	    if(new_row) {
		var cell=row.insertCell(-1);
		if(rx.snr>0) {
		    cell.innerHTML='+'+rx.snr;
		} else {
		    cell.innerHTML=rx.snr;
		}
		if(rx.snr>0) {
		    cell.style.backgroundColor=colors.snr_supergreen;
		} else if(rx.snr>=-10 && rx.snr<=0) {
		    cell.style.backgroundColor=colors.snr_green;
		} else if(rx.snr<-10 && rx.snr>=-17) {
		    cell.style.backgroundColor=colors.snr_yellow;
		} else {
		    cell.style.backgroundColor=colors.snr_red;
		}
	    }
	    
	    // speed
	    if(new_row) {
		var cell=row.insertCell(-1);
		var spd_img=false
		if(rx.speed==0) {
		    spd_img='/svg/transporter.svg';
		} else if(rx.speed==1) {
		    spd_img='/svg/mustang.svg';
		} else if(rx.speed==2) {
		    spd_img='/svg/911.svg';
		} else if(rx.speed==4) {
		    spd_img='/svg/kaefer.svg';
		}
		cell.innerHTML='<img src=\"'+spd_img+'\" width=\"24\" height=\"auto\"/>&nbsp;&nbsp;'+
		    english_speed(rx.speed);
	    }
	    
	    // frequency
	    if(new_row) {
		var cell=row.insertCell(-1);
		cell.innerHTML=rx.freq/1000.0;
	    }
	    
	    // text
	    if(new_row) {
		var cell=row.insertCell(-1);
		var tmp=rx.text.split(' ');
		var img=false;
		if(tmp[2]=='INFO' && tmp[3].search('CC=')!=-1) {
		    cell.style.backgroundColor=colors.non_zombie_traffic;
		    img='/jpg/ahrn.jpg';
		} else if(rx.to_call=='@AHRN') {
		    cell.style.backgroundColor=colors.non_zombie_traffic;
		    img='/jpg/ahrn.jpg';
		} else if(rx.to_call=='@SOTA') {
		    cell.style.backgroundColor=colors.non_zombie_traffic;
		    img='/jpg/sota.jpg';
		} else if(rx.to_call=='@POTA') {
		    cell.style.backgroundColor=colors.non_zombie_traffic;
		    img='/jpg/pota.jpg';
		} else if(rx.to_call=='@ARFCOM') {
		    cell.style.backgroundColor=colors.non_zombie_traffic;
		    img='/svg/ar.svg';
		} else if(rx.to_call=='@AMRRON' || rx.to_call=='@AMCON' ||
			  rx.to_call=='@AMRBB' || rx.to_call=='@AMRRFTX' ||
			  rx.to_call=='@AMRFTX' || rx.to_call=='@AMRNFTX') {
		    cell.style.backgroundColor=colors.non_zombie_traffic;
		    img='/jpg/amrron.jpg';
		} else if(rx.to_call=='@CORAC') {
		    cell.style.backgroundColor=colors.non_zombie_traffic;
		    img='/jpg/corac.jpg';
		} else if(tmp[2]=='HEARTBEAT' || rx.to_call=='@HB') {
		    cell.style.backgroundColor=colors.heartbeat;
		    img='/svg/zombie.svg'
		} else if(tmp[2]=='SNR' || tmp[2]=='SNR?' ||
			  tmp[2]=='INFO' || tmp[2]=='INFO?' ||
			  tmp[2]=='STATUS' || tmp[2]=='STATUS?' ||
			  tmp[2]=='HEARING' || tmp[2]=='HEARING?' ||
			  tmp[2]=='QUERY') {
		    img='/svg/gears.svg';
		    cell.style.backgroundColor=colors.query;
		} else if(tmp[2]=='MSG' || tmp[2]=='ACK') {
		    img='/svg/mail.svg';
		} else if(rx.to_call=='@ALLCALL' && tmp[2]=='CQ') {
		    cell.style.backgroundColor=colors.cq;
		    img='/svg/key.svg';
		} else if(rx.to_call=='@JS8CHESS') {
		    cell.style.backgroundColor=colors.non_zombie_traffic;
		    img='/svg/chess.svg';
		} else if(rx.to_call=='@SKYWARN') {
		    cell.style.backgroundColor=colors.non_zombie_traffic;
		    img='/svg/tornado.svg';
		} else if(rx.to_call=='@APRSIS' && tmp[3]==':SMSGTE') {
		    cell.style.backgroundColor=colors.cq;
		    img='/svg/sms.svg';
		} else if(rx.to_call=='@APRSIS' && tmp[3]==':EMAIL-2') {
		    cell.style.backgroundColor=colors.cq;
		    img='/svg/mail.svg';
		} else if(rx.to_call=='@APRSIS' || tmp[2]=='GRID' || tmp[2]=='GRID?') {
		    cell.style.backgroundColor=colors.non_zombie_traffic;
		    img='/svg/gps.svg';
		} else {
		    cell.style.backgroundColor=colors.non_zombie_traffic;
		    img='/svg/key.svg';
		}
		if(img) {
		    cell.innerHTML='<img src=\"'+img+'\" width=\"24\" height=\"24\"/>&nbsp;&nbsp;'+rx.text;
		} else {
		    cell.innerHTML=rx.text;
		}
	    }
	}
    }
    first_time=false
}, 1000);
