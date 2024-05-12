var pid = -1
init()


function clickHandler() {
	// Запуск процесса и получение PID
	fetch('http://127.0.0.1:5000/process')
	  .then(response => response.json())
	  .then(data => {
		pid = data.pid;
		console.log(pid)
		document.getElementById("loader").classList.add("active")
		// Запуск опроса (polling)
		const interval = setInterval(() => {
			fetch(`http://127.0.0.1:5000/check-process-grall/${pid}`).then(response => response.json()).then(data => {
				if (data.status === 'complete') {
					console.log(`Процесс ${pid} завершен!`);
					document.getElementById("loader").classList.remove("active")
					pid = -1
					clearInterval(interval);
					// Получение результатов или дальнейшие действия
				}
				else {
				  console.log('Процесс НЕ завершен');
				}
			});
		  }, 1000); // Опрос каждую секунду
	});
}
      
function stopHandler() {
	fetch(`http://127.0.0.1:5000//stop-process-grall/${pid}`).then(respone => respone.json()).then(data => {
		
		if (!data.result) {			
			console.log('Процесс c таким id не существует')
			return
		}
		
		console.log('Процесс отменен')
	})
	
	
	
}

function init() {
	document.getElementById('fileInput').addEventListener('change', function(e) {
		const file = e.target.files[0];
		
		if (!file) {
			return;
		}
	
		const reader = new FileReader();
		reader.onload = function(e) {
			const content = e.target.result;
			const jsonData = JSON.parse(content);
			var heat = L.heatLayer(jsonData.slice(2), {
				radius: 8,
				maxZoom: 15,
				max: 60
			}).addTo(map);
			map.setView([jsonData[0][0],jsonData[0][1]], 10)
			console.log(jsonData);
		};
	
		reader.readAsText(file);
	});
	
	
	
	var map = L.map("mapid").setView([51.5, -0.09], 10);
		L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
			attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
		}).addTo(map);
}