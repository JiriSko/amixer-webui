var controls;

var getJSON = function(url, successCallback, failCallback)
{
	var xhttp = new XMLHttpRequest();
	xhttp.onreadystatechange = function()
	{
		if (xhttp.readyState == 4 && xhttp.status == 200) {
			successCallback(JSON.parse(xhttp.responseText));
		} else if (xhttp.readyState == 4 && typeof failCallback !== "undefined") {
			failCallback(xhttp.status);
		}
	};
	xhttp.open('GET', url, true);
	xhttp.send();
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
				html += '<label class="mdl-checkbox mdl-js-checkbox mdl-js-ripple-effect" for="' + control.volume.id + '_lock"><input type="checkbox" id="' + control.volume.id + '_lock" class="mdl-checkbox__input" checked><span class="mdl-checkbox__label mdl-cell--hide-phone">Lock sliders</span></label>';
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
					html += '<span id="' + control.volume.id + '_channel_desc_' + i + '" class="value ' + control.volume.id + 'channel_desc' + '">' + Math.round(100 * control.volume.values[i] / control.volume.max) + '</span>&nbsp;%';
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

	if (document.getElementById(id + '_channel_desc_' + i)) {
		document.getElementById(id + '_channel_desc_' + i).innerHTML = value;
	}

	var isBgFlexPresent = document.getElementsByClassName(id + '_volume')[i].parentNode.childNodes.length === 2;
	if (isBgFlexPresent) {
		var bgFlexLower = document.getElementsByClassName(id + '_volume')[i].parentNode.childNodes[1].childNodes[0].style.flex;
		var bgFlexUpper = document.getElementsByClassName(id + '_volume')[i].parentNode.childNodes[1].childNodes[1].style.flex;
	}

	if ((document.getElementById(id + '_lock') && document.getElementById(id + '_lock').checked)
		|| (typeof id === 'string' && id.substr(0, 1) === 'e' && document.getElementById('equalizer_lock').checked)) {
		//console.log("Changed volume for all channel on control [id=" + id + "] to value: " + value)
		var volumeElements = document.getElementsByClassName(id + '_volume');
		var descElements = document.getElementsByClassName(id + 'channel_desc');
		for (var i = 0; i < volumeElements.length; i++) {
			volumeElements[i].value = value;
			if (descElements.length > 0) {
				descElements[i].innerHTML = Math.round(100 * value / volumeElements[i].getAttribute('max'));
			}
			if (isBgFlexPresent) {
				document.getElementsByClassName(id + '_volume')[i].parentNode.childNodes[1].childNodes[0].style.flex = bgFlexLower;
				document.getElementsByClassName(id + '_volume')[i].parentNode.childNodes[1].childNodes[1].style.flex = bgFlexUpper;
			}
			if (volumeElements[i].value == volumeElements[i].getAttribute('min')) {
				volumeElements[i].className += ' is-lowest-value';
			} else {
				volumeElements[i].className = volumeElements[i].className.replace(/is-lowest-value/, '');
			}
		}
	} else {
		//console.log("Changed volume on channel " + i + " on control [id=" + id + "] to value: " + value);
		document.getElementsByClassName(id + 'channel_desc')[0].innerHTML = Math.round(100 * value / document.getElementsByClassName(id + '_volume')[0].getAttribute('max'));
	}
	
	var elements = document.getElementsByClassName(id + '_volume');
	var volumes = [];
	for (var i = 0; i < elements.length; i++) {
		volumes.push(elements[i].value);
	}
	if (typeof id === "string" && id.substr(0, 1) === 'e') {
		sendRequest('PUT', "equalizer/" + id.substr(1) + "/" + volumes.join("/") + "/");
	} else {
		sendRequest('PUT', "volume/" + id + "/" + volumes.join("/") + "/");
	}
};

var changeCard = function (id)
{
	sendRequest('PUT', 'card/' + id + '/');
	document.getElementById('controls').innerHTML = '';
	loadControls();

	var cardSelects = document.getElementsByClassName('amixer-webui-cards');
	for (var i = 0; i < cardSelects.length; i++)
	{
		if (cardSelects[i].value != id) {
			cardSelects[i].value = id;
		}
	}
};

var loadCards = function ()
{
	getJSON('cards/', function(data)
	{
		if (Object.keys(data).length <= 1)
		{
			document.getElementsByClassName('mdl-layout__header-row')[1].remove();
			return;
		}

		var select = '<div class="mdl-textfield mdl-js-textfield"><select class="amixer-webui-cards mdl-textfield__input" onchange="changeCard(this.value)"><optgroup label="Sound card" class="mdl-cell--hide-desktop"></optgroup>';
		for (var i in data) {
			select += '<option value="' + i + '">' + data[i] + '</option>';
		}
		select += '</select></div>';

		document.getElementsByClassName('mdl-layout__header-row')[0].innerHTML += '<div class="mdl-cell--hide-phone"><span class="amixer-webui-sound-card__label mdl-cell--hide-tablet">Sound card:</span> ' + select + '</div>';
		document.getElementsByClassName('mdl-layout__header-row')[1].innerHTML += select;

		getJSON('card/?' + Date.now(), function(id)
		{
			if (id !== null)
			{
				var cardSelects = document.getElementsByClassName('amixer-webui-cards');
				for (var i = 0; i < cardSelects.length; i++) {
					cardSelects[i].value = id;
				}
			}
		});
	});
};

var loadEqualizer = function ()
{
	getJSON('equalizer/', function(data)
	{
		if (data && data.length)
		{
			var header = document.querySelectorAll('.mdl-layout__header .mdl-layout-spacer');
			header[0].outerHTML += '<button class="' + (header.length === 2 ? 'mdl-cell--hide-phone ' : '') + 'mdl-button mdl-js-button mdl-button--icon" title="Equalizer" onclick="document.querySelector(\'dialog\').showModal()"><i class="material-icons">equalizer</i></button>';
			if (header.length === 2) {
				header[1].outerHTML += '<button class="mdl-button mdl-js-button mdl-button--icon" title="Equalizer" onclick="document.querySelector(\'dialog\').showModal()"><i class="material-icons">equalizer</i></button>';
			}

			showEqualizer(data);
		}
	});

	var dialog = document.querySelector('dialog');
	if (!dialog.showModal) {
		dialogPolyfill.registerDialog(dialog);
	}
};

var showEqualizer = function (data)
{
	var html = '<div class="amixer-webui-equalizer">' +
		'<div class="amixer-webui-equalizer__container">';

	for (var i in data)
	{
		var match = data[i].name.match(/[0-9]+\. ([0-9]+ k?Hz) .*/);
		var name = match !== null ? match[1] : data[i].name;
		html += '<div class="amixer-webui-equalizer__name" title="' + data[i].name + '">' + name + '</div>';
		html += '<div class="amixer-webui-equalizer__band">';
		for (var j in data[i].channels)
		{
			html += '<input class="e' + data[i].id + '_volume mdl-slider mdl-js-slider" type="range" min="' + data[i].min + '" max="' + data[i].max + '" value="' + data[i].values[j] + '" title="' + data[i].channels[j] + '" onchange="changeVolume(\'e' + data[i].id + '\', ' + j + ', this.value)">';
		}
		html += '</div>';
	}

	html += '</div></div>';

	document.querySelector('.mdl-dialog__title').innerHTML = 'Equalizer';
	document.querySelector('.mdl-dialog__content').innerHTML = html;
	document.querySelector('.mdl-dialog__actions').innerHTML = '<button type="button" class="mdl-button mdl-js-button mdl-button--primary close">Close</button><label class="amixer-webui-equalizer__lock mdl-checkbox mdl-js-checkbox mdl-js-ripple-effect" for="equalizer_lock"><input type="checkbox" id="equalizer_lock" class="mdl-checkbox__input" checked><span class="mdl-checkbox__label">Lock sliders</span></label>';
	document.querySelector('.mdl-dialog__actions .close').addEventListener('click', function() {
		document.querySelector('dialog').close();
	});

	componentHandler.upgradeAllRegistered();
};

var loadControls = function()
{
	getJSON('controls/?' + Date.now(), function(data)
	{
		controls = getControls(data);

		document.body.className = document.body.className.replace(/\s?loading/, "");

		drawControls(controls);

		componentHandler.upgradeAllRegistered();

	}, function(status) {
		alert('Something went wrong.');
	});
};

document.addEventListener("DOMContentLoaded", function(event)
{
	loadCards();
	loadControls();
	loadEqualizer();
});
