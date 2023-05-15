var verbose=1;

// todo: list of flags heard

// This function takes in latitude and longitude of two location and
// returns the distance between them as the crow flies (in
// km). (Converted to miles - n0gq)
// https://stackoverflow.com/questions/18883601/function-to-calculate-distance-between-two-coordinates
function calcCrow(lat1,lon1,lat2,lon2) {
    var R=6371; // km
    var dLat=toRadians(lat2-lat1);
    var dLon=toRadians(lon2-lon1);
    var lat1=toRadians(lat1);
    var lat2=toRadians(lat2);

    var a=Math.sin(dLat/2) * Math.sin(dLat/2) +
	Math.sin(dLon/2) * Math.sin(dLon/2) * Math.cos(lat1) * Math.cos(lat2);
    var c=2 * Math.atan2(Math.sqrt(a),Math.sqrt(1-a));
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
function bearing(lat1,lon1,lat2,lon2){
    lat1=toRadians(lat1);
    lon1=toRadians(lon1);
    lat2=toRadians(lat2);
    lon2=toRadians(lon2);

    y=Math.sin(lon2 - lon1) * Math.cos(lat2);
    x=Math.cos(lat1) * Math.sin(lat2) -
	Math.sin(lat1) * Math.cos(lat2) * Math.cos(lon2 - lon1);
    brng=Math.atan2(y,x);
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

var call_groups=new Map(); // index is call, value is array of groups
var groups_call=new Map(); // index is groups, value is array of calls
var recent_at=new Map(); // Who has sent to @ lately? call=[@foo,time_t]
var display_groups=new Array();

// Add the specified call to the specified group if it's not already a member.
function add_call_to_group(call,group) {
    if(groups_call.get(group)) {
	if(!groups_call.get(group).includes(call)) {
	    groups_call.get(group).push(call);
	}
    } else {
	groups_call.set(group,[call]);
    }
}

// Add the specified call to the specified group if it's not already a member.
function add_group_to_call(call,group) {
    if(call_groups.get(call)) {
	if(!call_groups.get(call).includes(group)) {
	    call_groups.get(call).push(group);
	}
    } else {
	call_groups.set(call,[group]);
    }
}

// Update both calls and groups.
function update_calls_groups(call,group) {
    add_call_to_group(call,group);
    add_group_to_call(call,group);
    if(!display_groups.includes(group) && group!='@ALLCALL' && group!='@HB') {
	display_groups.push(group);
    }
}

// Does the group include this call?
function is_call_in_group(call,group) {
    if(groups_call.get(group).includes(call)) {
	return(true);
    } else {
	return(false);
    }
}

// Build a QRZ link for a call.
function qrz(call,linktext,icon) {
    if(icon) {
	return('<a href="https://qrz.com/db/'+call+'" target="_blank"><img src="/svg/globe.svg" alt="" width="15" height="15" />&nbsp;'+linktext+'</a>');
    } else {
	return('<a href="https://qrz.com/db/'+call+'" target="_blank">&nbsp;'+linktext+'</a>');
    }
}

// Build a Google Maps link for a location.
function gmaps(loc,linktext,icon) {
    if(icon) {
	return('<br /><a href="https://www.google.com/maps/search/?api=1&query='+encodeURIComponent(loc)+'" target="_blank"><img src="/svg/globe.svg" alt="" width="15" height="15" />&nbsp;'+linktext+'</a>');
    } else {
	return('<br /><a href="https://www.google.com/maps/search/?api=1&query='+encodeURIComponent(loc)+'" target="_blank">&nbsp;'+linktext+'</a>');
    }
}

// Build a pskreporter map link for a call.
function pskreporter(call,linktext,icon) {
    if(icon) {
	return('<a href="https://pskreporter.info/pskmap.html?preset&callsign='+call+'&timerange=1500&hideunrec=1&blankifnone=1&hidepink=1&showsnr=1&showlines=1" target="_blank"><img src="/svg/globe.svg" alt="" width="15" height="15" />&nbsp;'+linktext+'</a>');
    } else {
	return('<a href="https://pskreporter.info/pskmap.html?preset&callsign='+call+'&timerange=1500&hideunrec=1&blankifnone=1&hidepink=1&showsnr=1&showlines=1" target="_blank">&nbsp;'+linktext+'</a>');
    }
}


// Return unix time_t as an int.
function timet() {
    return(Math.floor(Date.now()/1000));
}

var first_time=true;

// Build the table contents page.
var intervalId=setInterval(async function() {
    // time_t
    var now=timet();
    
    if(first_time) {
	// Find the 'stations' table.
	var table=document.getElementById('stations');
	
	// Create the stations headers.
	var thead=document.createElement('thead');
	table.appendChild(thead);
	thead.appendChild(document.createElement('th')).appendChild(document.createTextNode('Call'));
	thead.appendChild(document.createElement('th')).appendChild(document.createTextNode('Grid'));
	thead.appendChild(document.createElement('th')).appendChild(document.createTextNode('Host'));
	thead.appendChild(document.createElement('th')).appendChild(document.createTextNode('Port'));
	thead.appendChild(document.createElement('th')).appendChild(document.createTextNode('Speed'));
	thead.appendChild(document.createElement('th')).appendChild(document.createTextNode('Dial'));
	thead.appendChild(document.createElement('th')).appendChild(document.createTextNode('Carrier'));
	thead.appendChild(document.createElement('th')).appendChild(document.createTextNode('Radio'));

	// Find the 'groups' table.
	var table=document.getElementById('groups');
	
	// Create the groups headers.
	var thead=document.createElement('thead');
	table.appendChild(thead);
	thead.appendChild(document.createElement('th')).appendChild(document.createTextNode('Group Name'));
	thead.appendChild(document.createElement('th')).appendChild(document.createTextNode('Count'));
	thead.appendChild(document.createElement('th')).appendChild(document.createTextNode('Members'));

	// Find the 'traffic' table.
	var table=document.getElementById('traffic');

	// Create the traffic headers.
	var thead=document.createElement('thead');
	table.appendChild(thead);
	thead.appendChild(document.createElement("th")).appendChild(document.createTextNode('Radio'));
	thead.appendChild(document.createElement("th")).appendChild(document.createTextNode('From'));
	thead.appendChild(document.createElement("th")).appendChild(document.createTextNode('Info'));
	thead.appendChild(document.createElement("th")).appendChild(document.createTextNode('To'));
	thead.appendChild(document.createElement("th")).appendChild(document.createTextNode('Info'));
	thead.appendChild(document.createElement("th")).appendChild(document.createTextNode('From Distance'));
	thead.appendChild(document.createElement("th")).appendChild(document.createTextNode('QSO Distance'));
	thead.appendChild(document.createElement("th")).appendChild(document.createTextNode('Age'));
	thead.appendChild(document.createElement("th")).appendChild(document.createTextNode('SNR'));
	thead.appendChild(document.createElement("th")).appendChild(document.createTextNode('Speed'));
	thead.appendChild(document.createElement("th")).appendChild(document.createTextNode('Frequency'));
	thead.appendChild(document.createElement("th")).appendChild(document.createTextNode('Received Text'));

	var mycall=false;
	var mygrid=false;
	var mylat=false;
	var mylon=false;
    }

    if(first_time || now%15==0) {
	// Get colors if we need them.
	if(!colors) {
	    try {
		// Get the color JSON.
		if(verbose>=1) { console.log('Fetching /colors'); }
		var color_response=await fetch('/colors');
		var color_stuff=await color_response.text();
		
		// Convert the text into JSON.
		var colors=JSON.parse(color_stuff);
	    }
	    catch(err) {
		console.log('Color error: '+err);
	    }
	}
	
	// Get friends if we need them.
	if(!friends) {
	    try {
		// Get the friends JSON.
		if(verbose>=1) { console.log('Fetching /friends'); }
		var friend_response=await fetch('/friends');
		var friend_stuff=await friend_response.text();
		
		// Convert the text into JSON.
		var friends=JSON.parse(friend_stuff);
	    }
	    catch(err) {
		console.log('Friends error: '+err);
	    }
	}
    
	try {
	    // Get the stuff JSON.
	    if(verbose>=1) { console.log('Fetching /json'); }
	    var stuff_response=await fetch('/json');
	    var stuff_stuff=await stuff_response.text();
	    
	    // Convert the text into JSON.
	    stuff=JSON.parse(stuff_stuff);
	    
	    if(verbose>0) { console.log(stuff); }
	}
	catch(err) {
	    console.log('Stuff error: '+err);
	}
	
	// Find my own lat/lon. ToDo: This could be much better. In
	// fact, this should work the same way as the 'from distance'
	// calculation. Fix.
	mycall=stuff.mycall;
	for (const [key, value] of Object.entries(stuff.stations)) {
	    if(value.stuff.call==mycall) {
		mygrid=value.stuff.grid;
		mylat=value.stuff.lat;
		mylon=value.stuff.lon;
	    }
	}

	// Find the 'groups' table.
	var table=document.getElementById('groups');
	for (var g in display_groups) {
	    var row=document.getElementById(display_groups[g]);
	    if(row) {
		var cell=row.cells[1];
		cell.innerHTML=groups_call.get(display_groups[g]).length;
		var cell=row.cells[2];
		var newg=new Array();
		groups_call.get(display_groups[g]).map(function (n) {
		    newg.push(qrz(n,n,false));
		});
		cell.innerHTML=newg.join(', ');
	    } else {
		row=table.insertRow(0);
		row.id=display_groups[g];
		var cell=row.insertCell(-1);
		cell.innerHTML=display_groups[g];
		var cell=row.insertCell(-1);
		cell.innerHTML=groups_call.get(display_groups[g]).length;
		var cell=row.insertCell(-1);
		var newg=new Array();
		groups_call.get(display_groups[g]).map(function (n) {
		    newg.push(qrz(n,n,false));
		});
		cell.innerHTML=newg.join(', ');
	    }
	}

	// Find the 'stations' table.
	var table=document.getElementById('stations');
	
	// Insert/update the radio info.
	for (var uuid in stuff['stations']) {
	    var row=document.getElementById(uuid);
	    if(row) {
		row.cells[0].innerHTML=stuff['stations'][uuid]['stuff']['call'];
		row.cells[1].innerHTML=stuff['stations'][uuid]['stuff']['grid'];
		row.cells[2].innerHTML=stuff['stations'][uuid]['stuff']['host'];
		row.cells[3].innerHTML=stuff['stations'][uuid]['stuff']['port'];
		row.cells[4].innerHTML=english_speed(stuff['stations'][uuid]['stuff']['speed']);
		row.cells[5].innerHTML=stuff['stations'][uuid]['stuff']['dial']/1000.0;
		row.cells[6].innerHTML=stuff['stations'][uuid]['stuff']['carrier'];
		row.cells[7].innerHTML=stuff['stations'][uuid]['stuff']['radio'];
	    } else {
		row=table.insertRow(0);
		row.id=uuid;
		var cell=row.insertCell(-1);
		cell.innerHTML=stuff['stations'][uuid]['stuff']['call'];
		var cell=row.insertCell(-1);
		cell.innerHTML=stuff['stations'][uuid]['stuff']['grid'];
		var cell=row.insertCell(-1);
		cell.innerHTML=stuff['stations'][uuid]['stuff']['host'];
		var cell=row.insertCell(-1);
		cell.innerHTML=stuff['stations'][uuid]['stuff']['port'];
		var cell=row.insertCell(-1);
		cell.innerHTML=english_speed(stuff['stations'][uuid]['stuff']['speed']);
		var cell=row.insertCell(-1);
		cell.innerHTML=stuff['stations'][uuid]['stuff']['dial']/1000.0;
		var cell=row.insertCell(-1);
		cell.innerHTML=stuff['stations'][uuid]['stuff']['carrier'];
		var cell=row.insertCell(-1);
		cell.innerHTML=stuff['stations'][uuid]['stuff']['radio'];
	    }
	}
    }

    // yyy
    first_time=false;

    // Find the 'traffic' table.
    var table=document.getElementById('traffic');
    
    // Sort the traffic by age.
    var tfc=stuff.traffic.sort(function(a, b){return a.stuff.time - b.stuff.time});
    var l=tfc.length;
    
    for(let i=0; i<l; i++) {
	let rx=tfc[i];
	var age=Math.round(now-rx.stuff.time)*1000;
	var row=document.getElementById(rx.id);
	if(!row) {
	    row=table.insertRow(0);
	    if(rx.id) {
		row.id=rx.id;
	    }
	    var new_row=true
	}
	if(new_row) {
	    // Radio
	    var cell=row.insertCell(-1);
	    cell.innerHTML=stuff.stations[rx.stuff.uuid]['stuff']['call']+'<br />'+stuff.stations[rx.stuff.uuid]['stuff']['radio'];
	    
	    // From
	    var cell=row.insertCell(-1);
	    var f=false;
	    if(friends) {
		if(Object.keys(friends).includes(rx.from_call)) {
		    f=friends[rx.from_call];
		}
	    }
	    if(rx.from_info) {
		var info='<br />'+rx.from_info;
	    } else {
		if(rx.from_country) {
		    var info='<br />'+rx.from_country;
		} else {
		    var info='';
		}
	    }
	    if(rx.from_call==mycall && mygrid) {
		cell.innerHTML='<img src="/flags/'+rx.from_flag+'" alt="" width="36" />&nbsp;&nbsp;'+rx.from_call+'<br />'+mygrid+info;
	    } else if(rx.from_grid==false) {
		cell.innerHTML='<img src="/flags/'+rx.from_flag+'" alt="" width="36" />&nbsp;&nbsp;'+rx.from_call+'<br />Grid: Unknown'+info;
	    } else {
		cell.innerHTML='<img src="/flags/'+rx.from_flag+'" alt="" width="36" />&nbsp;&nbsp;'+rx.from_call+'<br />Grid: '+rx.from_grid+info;
	    }
	    if(f) {
		if(f[1]!='') {
		    cell.style.backgroundColor=f[1];
		}
	    }
	    
	    // PSKR/QRZ/Map
	    var cell=row.insertCell(-1);
	    if(rx.from_addr) {
		var address=rx.from_addr;
	    } else {
		var address=rx.from_country;
	    }
	    cell.innerHTML=pskreporter(rx.from_call,'PSKR',true)+'<br />'+
		qrz(rx.from_call,'QRZ',true)+'<br />'+
		gmaps(address,'Map',true);
	    
	    // To
	    var cell=row.insertCell(-1);
	    var f=false;
	    if(friends) {
		if(Object.keys(friends).includes(rx.to_call)) {
		    f=friends[rx.to_call];
		}
	    }
	    if(rx.to_call[0]=='@') {
		cell.style.backgroundColor=colors.at;
		var flag=false;
		update_calls_groups(rx.from_call,rx.to_call);
		if(rx.to_call!='@HB' && rx.to_call!='@ALLCALL') {
		    recent_at.set(rx.from_call,[rx.to_call,rx.stuff.time]);
		}
	    } else {
		var flag=true;
	    }
	    if(rx.to_info) {
		var info='<br />'+rx.to_info;
	    } else {
		if(rx.to_country) {
		    var info='<br />'+rx.to_country;
		} else {
		    var info='';
		}
	    }
	    if(rx.to_call==mycall && mygrid) {
		cell.innerHTML='<img src="/flags/'+rx.to_flag+'" alt="" width="36" />&nbsp;&nbsp;'+rx.to_call+'<br />'+mygrid+info;
	    } else if(rx.to_grid==false) {
		if(flag) {
		    cell.innerHTML='<img src="/flags/'+rx.to_flag+'" alt="" width="36" />&nbsp;&nbsp;'+rx.to_call+'<br />Grid: Unknown'+info;
		} else {
		    cell.innerHTML=rx.to_call;
		}
	    } else {
		if(flag) {
		    cell.innerHTML='<img src="/flags/'+rx.to_flag+'" alt="" width="36" />&nbsp;&nbsp;'+rx.to_call+'<br />Grid: '+rx.to_grid+info;
		} else {
		    //cell.innerHTML=rx.to_call+'<br />'+rx.to_grid+info;
		    cell.innerHTML=rx.to_call+'<br />'+rx.to_grid+" This shouldn't happen";
		}
	    }
	    if(f) {
		if(f[1]!='') {
		    cell.style.backgroundColor=f[1];
		}
	    }
	    
	    // PSKR/QRZ/Map
	    var cell=row.insertCell(-1);
	    if(rx.to_addr) {
		var address=rx.to_addr;
	    } else {
		var address=rx.to_country;
	    }
	    if(rx.to_call[0]!='@') {
		cell.innerHTML=pskreporter(rx.to_call,'PSKR',true)+'<br />'+
		    qrz(rx.to_call,'QRZ',true)+'<br />'+
		    gmaps(address,'Map',true);
	    } else {
		cell.innerHTML='<img src="/svg/globe_grey.svg" alt="" width="24" height="24" />';
	    }
	    
	    // Src Distance
	    var cell=row.insertCell(-1);
	    if(rx.from_call==mycall) {
		cell.innerHTML='Me';
	    } else if(stuff.stations[rx.stuff.uuid].stuff.lat && stuff.stations[rx.stuff.uuid].stuff.lon && rx.from_lat && rx.from_lon) {
		var dist=Math.round(calcCrow(stuff.stations[rx.stuff.uuid].stuff.lat,stuff.stations[rx.stuff.uuid].stuff.lon,
					     rx.from_lat,rx.from_lon));
		var brg=Math.round(bearing(stuff.stations[rx.stuff.uuid].stuff.lat,stuff.stations[rx.stuff.uuid].stuff.lon,
					   rx.from_lat,rx.from_lon));
		if(dist<=75) {
		    cell.innerHTML='same grid';
		    cell.style.backgroundColor=colors.close;
		} else {
		    cell.innerHTML=dist+' mi @<br /> '+brg+' deg';
		}
	    } else {
		cell.innerHTML='';
		cell.style.backgroundColor=colors.grey;
	    }

	    // QSO Distance
	    var cell=row.insertCell(-1);
	    if(rx.from_lat && rx.from_lon && rx.to_call==mycall && mylat && mylon) {
		var dist=Math.round(calcCrow(rx.from_lat,rx.from_lon,mylat,mylon));
		if(dist<=75) {
		    cell.innerHTML='same grid';
		    cell.style.backgroundColor=colors.close;
		} else {
		    cell.innerHTML=dist+' mi';
		}
	    } else if(rx.from_lat && rx.from_lon && rx.to_lat && rx.to_lon) {
		var dist=Math.round(calcCrow(rx.from_lat,rx.from_lon,rx.to_lat,rx.to_lon));
		if(dist<=75) {
		    cell.innerHTML='same grid';
		    cell.style.backgroundColor=colors.close;
		} else {
		    cell.innerHTML=dist+' mi';
		}
	    } else {
		cell.innerHTML='';
		cell.style.backgroundColor=colors.grey;
	    }

	    // Age
	    var cell=row.insertCell(-1);
	    cell.innerHTML=new Date(age).toISOString().substr(11,8);
	    
	    // SNR
	    var cell=row.insertCell(-1);
	    if(rx.snr>0) {
		cell.innerHTML='+'+rx.snr+'dB';
	    } else {
		cell.innerHTML=rx.snr+'dB';
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
	    
	    // Speed
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
	    cell.innerHTML='<img src=\"'+spd_img+'\" width=\"36\" height=\"auto\"/><br />'+
		english_speed(rx.speed);
	    
	    // Freq
	    var cell=row.insertCell(-1);
	    cell.innerHTML=(rx.freq/1000.0).toFixed(3)+' khz';
	    
	    // Text
	    var cell=row.insertCell(-1);
	    var tmp=rx.text.split(' ');
	    var img=false;
	    var khz=rx.freq/1000.0;
	    if(tmp[2]=='INFO' && tmp[3].search('CC=')!=-1) {
		cell.style.backgroundColor=colors.non_zombie_traffic;
		img='/jpg/ahrn.jpg';
	    } else if(rx.to_call=='@AHRN' || rx.to_call=='@AMCON') {
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
	    } else if(rx.to_call=='@AMRRON' || rx.to_call=='@AMRBB' ||
		      rx.to_call=='@AMRRFTX' || rx.to_call=='@AMRFTX' ||
		      rx.to_call=='@AMRNFTX' || rx.to_call=='@CSTAT' ||
		      (khz >= 3588 && khz <= 5392) ||
		      (khz >= 7110 && khz <= 7114) ||
		      (khz >= 14110 && khz <= 14114)) {
		cell.style.backgroundColor=colors.non_zombie_traffic;
		// todo: revisit this (below)
		update_calls_groups(rx.from_call,'@AMRRON');
		if(rx.to_call[0]!='@') {
		    update_calls_groups(rx.to_call,'@AMRRON');
		}
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

	    // Process any replies to @ destinations.
	    if(recent_at.get(rx.to_call)) {
		if(recent_at.get(rx.to_call)[1]<=timet()-65) {
		    update_calls_groups(rx.from_call,recent_at.get(rx.to_call)[0]);
		}
	    }
	    // ToDo: Purge outdata data so it doesn't grow forever.

	} else {
	    // Age
	    var cell=row.cells[7];
	    cell.innerHTML=new Date(Math.round(now-rx.stuff.time)*1000).toISOString().substr(11,8);

	    // To
	    // Code below puts all calls in each instance of an @, but
	    // distorts the output. ToDo: Think about this.
//	    var cell=row.cells[3];
//	    if(rx.to_call[0]=='@' && rx.to_call!='@HB' && rx.to_call!='@ALLCALL') {
//		if(groups_call.get(rx.to_call)) {
//		    cell.innerHTML=rx.to_call+': '+groups_call.get(rx.to_call).join(', ');
//		}
//	    }
	}

	// Delete the expired traffic rows.
	var r=document.getElementById('traffic');
	for(let i=l; i<r.rows.length; i++) {
	    r.deleteRow(i);
	}
    }

    first_time=false;
},1000);
