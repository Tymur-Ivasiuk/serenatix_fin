if (window.NodeList && !NodeList.prototype.forEach) {
	NodeList.prototype.forEach = function (callback, thisArg) {
		thisArg = thisArg || window;
		for (var i = 0; i < this.length; i++) {
			callback.call(thisArg, this[i], i, this);
		}
	};
}

document.querySelectorAll('.select').forEach(function (dropDownWrapper) {
	const dropDownBtn = dropDownWrapper.querySelector('.select_header');
    const dropDownList = dropDownWrapper.querySelector('.select_list');
    const dropDownListItems = dropDownList.querySelectorAll('.select_item');
	const dropDownInput = dropDownWrapper.querySelector('.select_input-hidden');

	// Клик по кнопке. Открыть/Закрыть select
	dropDownBtn.addEventListener('click', function (e) {
		dropDownList.classList.toggle('is-active');
	});

	// Выбор элемента списка. Запомнить выбранное значение. Закрыть дропдаун
	dropDownListItems.forEach(function (listItem) {
		listItem.addEventListener('click', function (e) {
			e.stopPropagation();
			dropDownBtn.querySelector('.select_current').innerText = this.innerText;
            dropDownBtn.querySelector('.select_current').style.opacity = 1
			dropDownBtn.focus();
			dropDownInput.value = this.dataset.value;
			dropDownList.classList.remove('is-active');

		});
	});

	// Клик снаружи дропдауна. Закрыть дропдаун
	document.addEventListener('click', function (e) {
		if (e.target !== dropDownBtn) {
			dropDownList.classList.remove('is-active');
		}
	});

	// Нажатие на Tab или Escape. Закрыть дропдаун
	document.addEventListener('keydown', function (e) {
		if (e.key === 'Tab' || e.key === 'Escape') {
			dropDownList.classList.remove('is-active');
			dropDownBtn.blur();
		}
	});
});
