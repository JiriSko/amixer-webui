var controls;

var getJSON = function(url)
{
	return new Promise(function (resolve, reject)
	{
		var xhr = new XMLHttpRequest();
		xhr.open('GET', url, true);
		xhr.responseType = 'json';
		xhr.onload = function()
		{
			if (xhr.status === 200) {
				resolve(xhr.response);
			} else {
				reject(xhr.status);
			}
		};
		xhr.send();
	});
};

var sendRequest = function(mode, url)
{
	var xhr = new XMLHttpRequest();
	xhr.onreadystatechange = function() {
		if (xhr.readyState === 4 && xhr.status === 200) {
			document.body.className = document.body.className.replace(/\s?loading/, "");
		}
	};
	xhr.open(mode, url, true);
	xhr.send();
};


var getControl = function(array, name, iface)
{
	control = undefined;
	for (var i in array) {
		if (array[i].name === name) {
			control = array[i];
			break;
		}
	}
	
	if (control === undefined) {
		control = {name : name, iface : iface};
		array.push(control);
	}
	
	return control;
};

var getControls = function(data)
{
	//console.log(data);
	var controls = [];
	
	for (var i in data) {
		var el = data[i];
		regexp = new RegExp(' (' + ["Source", "Switch", "Volume"].join('|') + ')$');
		
		if (regexp.test(el.name)) { // connect multiple controls to one group if they are logically linked
			commonName = el.name.replace(regexp, "");
			var control = getControl(controls, commonName, el.iface);
			delete el.iface;
			control[el.name.replace(commonName + " ", "").toLowerCase()] = el;
		} else {
			var control = {};
			if (el.type === "ENUMERATED") {
				control = {source: el, name: el.name, iface: el.iface};
				delete control.source.iface;
			} else if (el.type === "BOOLEAN") {
				control = {switch: el, name: el.name, iface: el.iface};
				delete control.switch.iface;
			} else if (el.type === "INTEGER") {
				control = {volume: el, name: el.name, iface: el.iface};
				delete control.volume.iface;
			} else {
				control = {default: el, name: el.name, iface: el.iface};
				delete control.default.iface;
			}
			controls.push(control);
		}
	}
	
	//console.log(controls);
	return controls;
};

var drawControls = function(controls)
{
	//console.log(controls);
	
	var el = document.getElementById('controls');
	
	controls.forEach(function(control, control_index)
	{
		//console.log(control);
		if (control.iface === "MIXER") {
			var html = '<div class="amixer-webui-control mdl-color--white mdl-shadow--2dp mdl-cell mdl-cell--6-col mdl-cell--8-col-tablet mdl-cell--4-col-phone mdl-grid control_' + control_index + ' ' + (control.switch !== undefined ? (control.switch.values[0] ? 'on' : 'off') : '') + '">';
			html += '<div class="amixer-webui-control__title">';
			
			if (control.switch !== undefined) {
				var i = 0;
				html += '<label class="mdl-switch mdl-js-switch mdl-js-ripple-effect" for="' + control.switch.id + '_' + i + '_toggle"><input type="checkbox" id="' + control.switch.id + '_' + i + '_toggle"' + (control.switch.values[0] === true ? ' checked' : '') + ' onclick="toggleControl(' + control.switch.id + ', ' + i + ', ' + control_index + ')" class="mdl-switch__input"><span class="mdl-switch__label">';
			}
			
			html += '<h2 class="amixer-webui-control__title-text">' + control.name + '</h2>';
			
			if (control.switch !== undefined) {
				html += '</span></label>';
			}
			
			html += '<div class="mdl-layout-spacer"></div>';
			html += '<div>';
			
			if (control.volume !== undefined && control.volume.values.length > 1) {
				html += '<label class="mdl-checkbox mdl-js-checkbox mdl-js-ripple-effect" for="' + control.volume.id + '_bind"><input type="checkbox" id="' + control.volume.id + '_bind" class="mdl-checkbox__input" checked><span class="mdl-checkbox__label mdl-cell--hide-phone">Bind sliders</span></label>';
			}
			
			html += "</div>";
			html += "</div>";
			
			if (control.source !== undefined || control.volume !== undefined) {
				//html += '<hr>';
				html += '<div class="amixer-webui-control__actions">';
			}
			
			if (control.source !== undefined) {
				html += '<div class="enumerateList mdl-typography--text-center">';
				for (var i in control.source.items) {
					html += '<label class="mdl-radio mdl-js-radio mdl-js-ripple-effect" for="' + control.source.id + '_source_' + i + '"><input type="radio" id="' + control.source.id + '_source_' + i + '" name="' + control.source.id + '_source" onclick="changeSource(' + control.source.id + ', ' + i + ')" class="mdl-radio__button"' + (parseInt(i) === control.source.values[0] ? ' checked' : '') + '><span class="mdl-radio__label">' + control.source.items[i] + '</span></label>';
				}
				html += '</div>';
			}
			
			if (control.volume !== undefined) {
				for (var i in control.volume.values) {
					html += '<div class="volumes">';
					if (control.volume.channels !== undefined) {
						html += '<span class="channelDescription">' + control.volume.channels[i] + '</span>';
					}
					html += '<input type="range" min="' + control.volume.min + '" max="' + control.volume.max + '" stype="' + control.volume.step + '" value="' + control.volume.values[i] + '" onchange="changeVolume(' + control.volume.id + ', ' + i + ', this.value)" class="' + control.volume.id + '_volume mdl-slider mdl-js-slider">';
					html += '<span id="' + control.volume.id + '_channel_desc_' + i + '" class="value ' + control.volume.id + 'channel_desc' + '">' + control.volume.values[i] + '</span>';
					html += '</div>';
				}
			}
			
			if (control.source !== undefined || control.volume !== undefined) {
				html += "</div>";
			}
			html += "</div>\n";
			el.innerHTML += html;
		} else {
//			el.innerHTML += "<div class='amixer-webui-control mdl-color--white mdl-shadow--2dp mdl-cell mdl-cell--6-col mdl-cell--8-col-tablet mdl-cell--4-col-phone mdl-grid'><div class='amixer-webui-control__title'><h2 class='amixer-webui-control__title-text'>" + control.name + "</div></div></div>\n";
		}
	});
};


var toggleControl = function(id, i, control_index)
{
	document.body.className += " loading";
	
	var checked = document.getElementById(id + '_' + i + '_toggle').checked;
	//console.log("Turn " + (checked ? "on" : "off") + " control [id=" + id + ",index=" + i + "]");
	
	var control = document.getElementsByClassName('control_' + control_index)[0];
	control.className = control.className.replace(/ (on|off)/, ' ' + (checked ? 'on' : 'off'));
	
	sendRequest('PUT', "control/" + id + "/" + (checked ? 1 : 0) + "/");
};

var changeSource = function(id, value)
{
	document.body.className += " loading";
	
	//console.log("Changed source [id=" + id + "] to value: " + value);
	sendRequest('PUT', "source/" + id + "/" + value + "/");
};

var changeVolume = function(id, i, value)
{
	document.body.className += " loading";
	
	document.getElementById(id + '_channel_desc_' + i).innerHTML = value;
	
	var bgFlexLower = document.getElementsByClassName(id + '_volume')[i].parentNode.childNodes[1].childNodes[0].style.flex;
	var bgFlexUpper = document.getElementsByClassName(id + '_volume')[i].parentNode.childNodes[1].childNodes[1].style.flex;
	
	if (document.getElementById(id + '_bind') && document.getElementById(id + '_bind').checked) {
		//console.log("Changed volume for all channel on control [id=" + id + "] to value: " + value)
		var volumeElements = document.getElementsByClassName(id + '_volume');
		var descElements = document.getElementsByClassName(id + 'channel_desc');
		for (var i = 0; i < volumeElements.length; i++) {
			volumeElements[i].value = value;
			descElements[i].innerHTML = value;
			document.getElementsByClassName(id + '_volume')[i].parentNode.childNodes[1].childNodes[0].style.flex = bgFlexLower;
			document.getElementsByClassName(id + '_volume')[i].parentNode.childNodes[1].childNodes[1].style.flex = bgFlexUpper;
		}
	} else {
		//console.log("Changed volume on channel " + i + " on control [id=" + id + "] to value: " + value);
	}
	
	var elements = document.getElementsByClassName(id + '_volume');
	var volumes = [];
	for (var i = 0; i < elements.length; i++) {
		volumes.push(elements[i].value);
	}
	sendRequest('PUT', "volume/" + id + "/" + volumes.join("/") + "/");
};



document.addEventListener("DOMContentLoaded", function(event)
{
	getJSON('controls/').then(function(data)
	{
		controls = getControls(data);
		
		document.body.className = document.body.className.replace(/\s?loading/, "");
		
		drawControls(controls);
		
		componentHandler.upgradeAllRegistered();
		
	}, function(status) {
		alert('Something went wrong.');
	});
});