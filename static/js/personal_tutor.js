function addTutorSubject() {							
            
            // Создаем объект данных для отправки
            var selectSubjects = document.getElementById("select1");
			var selectedOption = selectSubjects.options[selectSubjects.selectedIndex];
			
			$.ajax({
                    url: '/add_subject',
                    method: 'POST',
                    data: {'subject': selectedOption.value},
                    success: function(response) {
                        window.location.href = '/personal_tutor';						
                    },
                    error: function(xhr, status, error) {
                        console.log('Ошибка:', error);
                    }
                });
}

function removeTutorSubject(subject_id) {           	
			$.ajax({
                    url: '/remove_subject',
                    method: 'POST',
                    data: {'subject': subject_id},
                    success: function(response) {
                        window.location.href = '/personal_tutor';						
                    },
                    error: function(xhr, status, error) {
                        console.log('Ошибка:', error);
                    }
                });
}
			
     