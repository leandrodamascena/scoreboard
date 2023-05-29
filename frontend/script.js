// JavaScript function to change the active tab and show the corresponding content
function changeTab(tabIndex) {
  // Get all tab buttons and contents
  var tabButtons = document.getElementsByClassName("tab");
  var tabContents = document.getElementsByClassName("tab-content");

  // Remove "active" class from all tab buttons and contents
  for (var i = 0; i < tabButtons.length; i++) {
    tabButtons[i].classList.remove("active");
    tabContents[i].classList.remove("active");
  }

  // Add "active" class to the selected tab button and content
  console.log(tabIndex)
  if (tabIndex != undefined) {
      tabButtons[tabIndex].classList.add("active");
      tabContents[tabIndex].classList.add("active");
  }
  // Perform AJAX call to update the table data
  updateTableData(tabIndex);
}

// Function to update table data using AJAX
function updateTableData(tabIndex) {
  var tableId = "tab" + tabIndex + "-table";
  var table = document.getElementById(tableId);

  // Simulating AJAX call to retrieve updated data
  // Replace this with your actual AJAX call to fetch data from the server
  $.ajax({
    url: "https://jcd53v2o3j.execute-api.us-east-1.amazonaws.com/dev/score",
    //headers: {"x-api-key": "YNMZYrXTdv59s9ZnngG9o4rBnbmm3bZ55VDEA8eg"},
    type: "GET",
    success: function(data) {
      // Update the table content
      var tableBody = table.getElementsByTagName("tbody")[0];
      tableBody.innerHTML = "";

      

      for (var i = 0; i < data.length; i++) {
        console.log(data[i].player_name)
        var row = "<tr>" +
                  "<td>" + data[i].player_name["S"] + "</td>" +
                  "<td>" + data[i].score["N"] + "</td>" +
                  "<td>" + data[i].player_country["S"] + "</td>" +
                  "<td>" + data[i].player_os["S"] + "</td>" +
                  "</tr>";
        tableBody.innerHTML += row;
      }
    },
    error: function() {
      console.log("Error occurred during AJAX call.");
    }
  });
}

// Initial call to update the default active tab
changeTab(0);

// Set interval to update the tables every 5 seconds (5000 milliseconds)
setInterval(function() {
  // Get the active tab index
  var activeTab = document.getElementsByClassName("tab active")[0];
  var activeTabIndex = Array.from(activeTab.parentNode.children).indexOf(activeTab);

  // Update the table data for the active tab
  updateTableData(activeTabIndex);
}, 5000);


// Sort table data based on column index and ascending/descending order
function sortTable(tabIndex, columnIndex) {
  var tableId = "tab" + tabIndex + "-table";
  var table = document.getElementById(tableId);
  var tableBody = table.getElementsByTagName("tbody")[0];
  var rows = Array.from(tableBody.getElementsByTagName("tr"));

  // Sort the rows based on the column values
  rows.sort(function(a, b) {
    var valueA = a.getElementsByTagName("td")[columnIndex].innerText;
    var valueB = b.getElementsByTagName("td")[columnIndex].innerText;

    if (columnIndex === 1) {
      valueA = parseInt(valueA);
      valueB = parseInt(valueB);
    }

    if (valueA < valueB) {
      return -1;
    } else if (valueA > valueB) {
      return 1;
    } else {
      return 0;
    }
  });

  // Reverse the order if the table is already sorted in ascending order
  // if (table.classList.contains("sorted-asc")) {
  //   rows.reverse();
  //   table.classList.remove("sorted-asc");
  //   table.classList.add("sorted-desc");
  // } else {
  //   table.classList.remove("sorted-desc");
  //   table.classList.add("sorted-asc");
  // }

  // Re-append the sorted rows to the table
  tableBody.innerHTML = "";
  for (var i = 0; i < rows.length; i++) {
    tableBody.appendChild(rows[i]);
  }
}
