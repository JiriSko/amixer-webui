<!DOCTYPE html>
<html>
<head>
	<meta charset="utf-8">
	
	<title>ALSA Mixer WebUI on {$hostname}</title>
	
	<meta name="viewport" content="width=device-width, initial-scale=1.0">
	
	<link rel="stylesheet" href="css/material.teal-cyan.min.css" />
	<link rel="stylesheet" href="css/material-icons.css">
	<link rel="stylesheet" href="css/style.css">
	
	<script src="js/script.js"></script>
	<script src="js/material.min.js"></script>
	
	<link rel="apple-touch-icon" sizes="57x57" href="icons/apple-touch-icon-57x57.png">
	<link rel="apple-touch-icon" sizes="60x60" href="icons/apple-touch-icon-60x60.png">
	<link rel="apple-touch-icon" sizes="72x72" href="icons/apple-touch-icon-72x72.png">
	<link rel="apple-touch-icon" sizes="76x76" href="icons/apple-touch-icon-76x76.png">
	<link rel="apple-touch-icon" sizes="114x114" href="icons/apple-touch-icon-114x114.png">
	<link rel="apple-touch-icon" sizes="120x120" href="icons/apple-touch-icon-120x120.png">
	<link rel="apple-touch-icon" sizes="144x144" href="icons/apple-touch-icon-144x144.png">
	<link rel="apple-touch-icon" sizes="152x152" href="icons/apple-touch-icon-152x152.png">
	<link rel="apple-touch-icon" sizes="180x180" href="icons/apple-touch-icon-180x180.png">
	<link rel="icon" type="image/png" href="icons/favicon-32x32.png" sizes="32x32">
	<link rel="icon" type="image/png" href="icons/favicon-194x194.png" sizes="194x194">
	<link rel="icon" type="image/png" href="icons/favicon-96x96.png" sizes="96x96">
	<link rel="icon" type="image/png" href="icons/android-chrome-192x192.png" sizes="192x192">
	<link rel="icon" type="image/png" href="icons/favicon-16x16.png" sizes="16x16">
	<link rel="manifest" href="icons/manifest.json">
	<link rel="mask-icon" href="icons/safari-pinned-tab.svg" color="#5bbad5">
	<link rel="shortcut icon" href="icons/favicon.ico">
	<meta name="msapplication-TileColor" content="#ffffff">
	<meta name="msapplication-TileImage" content="icons/mstile-144x144.png">
	<meta name="msapplication-config" content="icons/browserconfig.xml">
	<meta name="theme-color" content="#009688">
</head>

<body class="loading">
	
	<div class="mdl-layout mdl-js-layout mdl-layout--fixed-header">
		
		<div class="mdl-layout__header">
			<header class="mdl-layout__header-row">
				<h1 class="mdl-layout-title">
					ALSA Mixer WebUI on {$hostname}
				</h1>
			</header>
		</div>
		
		<main class="mdl-layout__content">
			<div class="mdl-grid" id="controls"></div>
		</main>
	
	</div>
	
	<div class="amixer-webui-spinner">
		<div class="mdl-spinner mdl-spinner--single-color mdl-js-spinner is-active"></div>
	</div>
	
</body>
</html>
