function sendQuery() {
	var selectSubjects = document.getElementById("select2");
	var subject_id = selectSubjects.options[selectSubjects.selectedIndex].value;
	var theme = document.getElementById("nq_theme").value;
	var qtext = document.getElementById("nq_text").value;
			
	$.ajax({
		url: '/add_query',
		method: 'POST',
		data: {'subject_id': subject_id,
			   'theme': theme,
			   'qtext': qtext},
		success: function(response) {
			window.location.href = '/';	
		},
		error: function(xhr, status, error) {
			console.log('Ошибка:', error);
		}
	});
}

async function newQuery() {
		var response = await fetch('/get_allsubjects');	
		var data = await response.json();		
		var subjects = data.subjects;				
		var htmlrequestDetail = '<center><h1>Предмет<br><select id="select2" type="text"><br>';
		for (var i = 0; i < subjects.length; i++) {						
			htmlrequestDetail += '<option value="' + subjects[i][0] + '">' + subjects[i][1] + '</option>'
		}
		htmlrequestDetail += '</select><br>Тема<br><input id="nq_theme" type="text" required><br>'
		htmlrequestDetail += 'Текст заявки<br><textarea id="nq_text" cols=40 rows=15></textarea><br>'
		htmlrequestDetail += '<button onclick=sendQuery()>Отправить заявку</button>';
		htmlrequestDetail += '</h1></center>';			
        $('#requestOne').html(htmlrequestDetail);				
	  }

async function acceptRequest(request_id)	{
	$.ajax({
		url: '/accept_request',
		method: 'POST',
		data: {'request_id': request_id},
		success: function(response) {
			window.location.href = '/';	
		},
		error: function(xhr, status, error) {
			console.log('Ошибка:', error);
		}
	});
}

async function confirmRequest(request_id)	{
	$.ajax({
		url: '/confirm_request',
		method: 'POST',
		data: {'request_id': request_id},
		success: function(response) {
			window.location.href = '/';	
		},
		error: function(xhr, status, error) {
			console.log('Ошибка:', error);
		}
	});
}

async function finishRequest(request_id)	{
	$.ajax({
		url: '/finish_request',
		method: 'POST',
		data: {'request_id': request_id},
		success: function(response) {
			window.location.href = '/';	
		},
		error: function(xhr, status, error) {
			console.log('Ошибка:', error);
		}
	});
}

function requestclientList() {
	var selectedRequestId = null;
	var modeNewRequest = false;
		
      // Функция для получения списка заявок
      async function getRequests() {
        var response = await fetch('/get_clientrequestlist');
        var data = await response.json();
        var requestlist = data.requestlist;				
        var table = '<table><tr><th>Предмет</th><th>Тема</th><th>Статус</th><th>Время</th></tr>';
        for (var i = 0; i < requestlist.length; i++) {
		  var requestId = requestlist[i][0]; // id
		  if (requestId == selectedRequestId) {
			  var row = '<tr class="client-request-row selected" data-id="' + requestId + '">';
		  }
		  else {
			var row = '<tr class="client-request-row" data-id="' + requestId + '">';
		  }
          row += '<td>' + requestlist[i][1] + '</td><td>' + requestlist[i][2] + '</td><td>' + requestlist[i][3] + '</td><td>' + requestlist[i][4] + '</td>';
		  row += '</tr>';
          table += row;
        }
		table += '</table>';
        $('#requestlist-table').html(table);        		
      }

      // Функция для получения деталей заявки
      async function getRequestDetails(requestId) {				
		if (requestId) {
			var response = await fetch('/get_request_details/' + requestId);
			var data = await response.json();
			var requestDetails = data.query;
			
			var htmlrequestDetail = '';			
			htmlrequestDetail += '<center><h1>'        
			if (requestDetails[3] == 0) {
				htmlrequestDetail += '<button class="transparent-button"><img src="static/images/white_circle.png" width="50" height="50"><h1>Ожидает принятия репетитором</h1></button><br>';
				document.getElementById("chat").style.visibility = "hidden";
			}
			else if (requestDetails[3] == 1) {
				htmlrequestDetail += '<button class="transparent-button" onclick="confirmRequest(' + requestId + ')"><img src="static/images/orange_circle.png" width="50" height="50"><h1>Принята репетитором<br>Подтвердить</h1></button><br>';
				document.getElementById("chat").style.visibility = "hidden";
			}
			else if (requestDetails[3] == 2) {
				htmlrequestDetail += '<button class="transparent-button")><img src="static/images/blue_circle.png" width="50" height="50"><h1>Заявка в работе</h1></button><br>';
				document.getElementById("chat").style.visibility = "visible";
			}
			else if (requestDetails[3] == 3) {
				htmlrequestDetail += '<button class="transparent-button"><img src="static/images/green_circle.png" width="50" height="50"><h1>Завершена</h1></button><br>';
				document.getElementById("chat").style.visibility = "hidden";
			}
			htmlrequestDetail += requestDetails[0] + '<br>';
			htmlrequestDetail += requestDetails[1] + '<br>';
			htmlrequestDetail += requestDetails[2] + '<br>';
			htmlrequestDetail += '</h1></center>';
		}		
        $('#requestOne').html(htmlrequestDetail);
      }

      // Обработчик клика на заявку в таблице заявок
      $(document).on('click', '#requestlist-table tr[data-id]', function() {
        var requestId = $(this).data('id');
		// Удаление класса выделения с предыдущей выбранной строки
		if (selectedRequestId != requestId) {	
			if (selectedRequestId) {
			$('#requestlist-table tr[data-id="' + selectedRequestId + '"]').removeClass('selected');
			}
			// Добавление класса выделения к текущей выбранной строке
			$(this).addClass('selected');		
			selectedRequestId = requestId;
		getRequestDetails(requestId);
		}        
      });

      // Периодически обновлять статус заявок каждые 5 секунд
      setInterval(getRequests, 5000);

      // Инициализация страницы
	  document.getElementById("chat").style.visibility = "hidden";
      getRequests();
	  getRequestDetails(null);
    }

function requesttutorList() {
	var selectedRequestId = null;
	var modeNewRequest = false;	
      // Функция для получения списка заявок
      async function getRequests() {
        var response = await fetch('/get_tutorrequestlist');
        var data = await response.json();				
        var requestlist1 = data.requestlist['t1'];		
		var htmltext = '<center>Новые заявки</center>';
        htmltext += '<table><tr><th>Предмет</th><th>Тема</th><th>Статус</th><th>Время</th></tr>';		
        for (var i = 0; i < requestlist1.length; i++) {
		  var requestId = requestlist1[i][0]; // id
		  if (requestId == selectedRequestId) {
			  var row = '<tr class="client-request-row selected" data-id="' + requestId + '">';
		  }
		  else {
			var row = '<tr class="client-request-row" data-id="' + requestId + '">';
		  }
          row += '<td>' + requestlist1[i][1] + '</td><td>' + requestlist1[i][2] + '</td><td>' + requestlist1[i][3] + '</td><td>' + requestlist1[i][4] + '</td>';
		  row += '</tr>';
          htmltext += row;
        }
		htmltext += '</table>';
		var requestlist2 = data.requestlist['t2'];				
		htmltext += '<center>Мои заявки</center>'
        htmltext += '<table><tr><th>Предмет</th><th>Тема</th><th>Статус</th><th>Время</th></tr>';
        for (var i = 0; i < requestlist2.length; i++) {
		  var requestId = requestlist2[i][0]; // id
		  if (requestId == selectedRequestId) {
			  var row = '<tr class="client-request-row selected" data-id="' + requestId + '">';
		  }
		  else {
			var row = '<tr class="client-request-row" data-id="' + requestId + '">';
		  }
          row += '<td>' + requestlist2[i][1] + '</td><td>' + requestlist2[i][2] + '</td><td>' + requestlist2[i][3] + '</td><td>' + requestlist2[i][4] + '</td>';
		  row += '</tr>';
          htmltext += row;
        }
		htmltext += '</table>';
        $('#requestlist-table').html(htmltext);
      }

      // Функция для получения деталей заявки
      async function getRequestDetails(requestId) {				
		if (requestId) {						
			var response = await fetch('/get_request_details/' + requestId);
			var data = await response.json();
			var requestDetails = data.query;
			
			var htmlrequestDetail = '';			
			htmlrequestDetail += '<center><h1>'        
			if (requestDetails[3] == 0) {
				htmlrequestDetail += '<button class="transparent-button" onclick="acceptRequest(' + requestId + ')"><img src="static/images/white_circle.png" width="50" height="50"><h1>Принять</h1></button><br>';
				document.getElementById("chat").style.visibility = "hidden";
			}
			else if (requestDetails[3] == 1) {
				htmlrequestDetail += '<button class="transparent-button"><img src="static/images/orange_circle.png" width="50" height="50"><h1>Ожидает подтверждения клиента</h1></button><br>';
				document.getElementById("chat").style.visibility = "hidden";
			}
			else if (requestDetails[3] == 2) {
				htmlrequestDetail += '<button class="transparent-button" onclick="finishRequest(' + requestId + ')"><img src="static/images/blue_circle.png" width="50" height="50"><h1>Заявка в работе<br>Завершить</h1></button><br>';
				document.getElementById("chat").style.visibility = "visible";
			}
			else if (requestDetails[3] == 3) {
				htmlrequestDetail += '<button class="transparent-button"><img src="static/images/green_circle.png" width="50" height="50"><h1>Завершена</h1></button><br>';
				document.getElementById("chat").style.visibility = "hidden";
			}
			htmlrequestDetail += requestDetails[0] + '<br>';
			htmlrequestDetail += requestDetails[1] + '<br>';
			htmlrequestDetail += requestDetails[2] + '<br>';
			htmlrequestDetail += '</h1></center>';
		}		
        $('#requestOne').html(htmlrequestDetail);
      }

      // Обработчик клика на заявку в таблице заявок
      $(document).on('click', '#requestlist-table tr[data-id]', function() {
        var requestId = $(this).data('id');
		// Удаление класса выделения с предыдущей выбранной строки
		if (selectedRequestId != requestId) {	
			if (selectedRequestId) {
			$('#requestlist-table tr[data-id="' + selectedRequestId + '"]').removeClass('selected');
			}
			// Добавление класса выделения к текущей выбранной строке
			$(this).addClass('selected');		
			selectedRequestId = requestId;
		getRequestDetails(requestId);
		}        
      });

      // Периодически обновлять статус заявок каждые 5 секунд
      setInterval(getRequests, 5000);

      // Инициализация страницы
	  document.getElementById("chat").style.visibility = "hidden";
      getRequests();
	  getRequestDetails(null);
}

function sqlrequest() {

	var sqlrequest = document.getElementById("sqlrequest").value;
	alert(sqlrequest);

	$.ajax({
		url: '/add_query',
		method: 'POST',
		data: {'subject_id': subject_id,
			   'theme': theme,
			   'qtext': qtext},
		success: function(response) {
			window.location.href = '/';
		},
		error: function(xhr, status, error) {
			console.log('Ошибка:', error);
		}
	});
}