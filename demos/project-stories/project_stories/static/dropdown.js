/*
 * This JavaScript module is based on the code available at
 * https://www.w3schools.com/howto/howto_custom_select.asp.
 */

window.initDropdown = (elemId, onChange, shallDelegate) => {
  const dropdown = document.getElementById(elemId);
  if (dropdown) {
    const select = dropdown.getElementsByTagName("select")[0];

    // For each element, create a new div that will act as the selected item.
    const opt_sel = document.createElement("div");
    opt_sel.setAttribute("class", "option-selected");
    opt_sel.innerHTML = select.options[select.selectedIndex].innerHTML;
    dropdown.appendChild(opt_sel);

    // For each element, create a new DIV that will contain the option list.
    const items = document.createElement("div");
    items.setAttribute("class", "select-items select-hide");

    for (let j = 0; j < select.length; j++) {
      // For each option in the original select element,
      // create a new DIV that will act as an option item.
      const opt_div = document.createElement("div");
      opt_div.innerHTML = select.options[j].innerHTML;
      opt_div.setAttribute("data-value", select.options[j].value);
      opt_div.addEventListener(
        "click", selectItemClosure(onChange, shallDelegate));
      items.appendChild(opt_div);
    }
    dropdown.appendChild(items);
    opt_sel.addEventListener("click", function(e) {
      // When the select box is clicked, close any other
      // select boxes, and open/close the current select box.
      e.stopPropagation();
      closeAllSelect(this);
      this.nextSibling.classList.toggle("select-hide");
      this.classList.toggle("select-arrow-active");
    });

    // Make a default selection.
    opt_sel.innerHTML = select.options[select.selectedIndex].innerHTML;
    const item_sel = items.children[select.selectedIndex];
    item_sel.setAttribute("class", "same-as-selected");
  }

  // If the user clicks anywhere outside the
  // select box, then close all select boxes.
  document.addEventListener("click", closeAllSelect);
}

function selectItemClosure(onChange, shallDelegate) {
  function selectItem(ev) {
    // When an item is clicked, update the original
    // select box and the selected item.
    let shallCallOnChange = false;
    const select = this.parentNode.parentNode.getElementsByTagName("select")[0];
    const opt_sel = this.parentNode.previousSibling;
    for (let idx = 0; idx < select.length; idx++) {
      if (select.options[idx].innerHTML == this.innerHTML) {
        shallCallOnChange = true;
        if (onChange && shallDelegate) {
          return onChange(ev);
        } else {
          select.selectedIndex = idx;
          opt_sel.innerHTML = this.innerHTML;
          const items = this.parentNode
            .getElementsByClassName("same-as-selected");
          for (let jdx = 0; jdx < items.length; jdx++) {
            items[jdx].removeAttribute("class");
          }
          this.setAttribute("class", "same-as-selected");
          break;
        }
      }
    }
    opt_sel.click();
    if (shallCallOnChange) {
      onChange(ev);
    }
  }
  return selectItem;
}


function closeAllSelect(element) {
  // A function that will close all select boxes
  // in the document, except the current select box.
  var arrNo = [];
  const items = document.getElementsByClassName("select-items");
  const opt_sel = document.getElementsByClassName("option-selected");
  for (let i = 0; i < opt_sel.length; i++) {
    if (element == opt_sel[i]) {
      arrNo.push(i)
    } else {
      opt_sel[i].classList.remove("select-arrow-active");
    }
  }
  for (let i = 0; i < items.length; i++) {
    if (arrNo.indexOf(i)) {
      items[i].classList.add("select-hide");
    }
  }
}
