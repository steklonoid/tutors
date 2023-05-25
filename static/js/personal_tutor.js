function addTutorSubject() {							
            // Создаем новый объект XMLHttpRequest
            /*var xhr = new XMLHttpRequest();
			
			xhr.onload = function() {
				
                if (xhr.status === 200) {
                    // Здесь можно обработать успешный ответ сервера
                    window.Location.reload();
                } else {
                    // Здесь можно обработать ошибку
                    console.error('Произошла ошибка: ' + xhr.status);
                }
            };
			
            // Открываем соединение и устанавливаем метод и URL-адрес
            xhr.open('POST', '/add_subject', true);

            // Устанавливаем заголовки, если необходимо
            xhr.setRequestHeader('Content-Type', 'application/json');*/

            // Создаем объект данных для отправки
            var selectSubjects = document.getElementById("select1");
			var selectedOption = selectSubjects.options[selectSubjects.selectedIndex];
			
			/*data = {'subject': selectedOption.value}
			
            // Преобразуем объект данных в JSON-строку
            var jsonData = JSON.stringify(data); 

            // Отправляем POST-запрос с данными
            xhr.send(jsonData);*/
			
			$.ajax({
                    url: '/add_subject',
                    method: 'POST',
                    data: {'subject': selectedOption.value},
                    success: function(response) {
                        window.location.reload(); // Обновление страницы
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
                        window.location.reload(); // Обновление страницы
                    },
                    error: function(xhr, status, error) {
                        console.log('Ошибка:', error);
                    }
                });
}
			
     