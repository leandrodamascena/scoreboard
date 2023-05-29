const API_KEY = "IdsK5c4xBf3m1AHbol1Nq7ag0GRPqnTE592pwGoJ"
const API_URL = "https://wdzyqmxvt7.execute-api.us-east-1.amazonaws.com/dev/score"
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
  if (tabIndex !== undefined) {
    tabButtons[tabIndex].classList.add("active");
    tabContents[tabIndex].classList.add("active");
  }

  // Perform AJAX call to update the table data
  if (tabIndex === 1) {
    // Per Country tab
    updateCountryTab();
  } else {
    updateTableData(tabIndex);
  }
}

// Function to update table data using AJAX
function updateTableData(tabIndex) {
  var tableId = "tab" + tabIndex + "-table";
  var table = document.getElementById(tableId);

  if (!table) {
    console.log("Table not found");
    return;
  }

  // Simulating AJAX call to retrieve updated data
  // Replace this with your actual AJAX call to fetch data from the server
  $.ajax({
    url: API_URL,
    type: "GET",
    headers: {"x-api-key": API_KEY},
    xhrFields: {
      withCredentials: true
    },
    beforeSend: function(xhr) {
      xhr.setRequestHeader("x-api-key", API_KEY);
  },
    crossDomain: true,
    success: function(data) {
      // Update the table content
      var tableBody = table.getElementsByTagName("tbody")[0];
      tableBody.innerHTML = "";

      for (var i = 0; i < data.length; i++) {
        var row =
          "<tr>" +
          "<td>" +
          data[i].player_name["S"] +
          "</td>" +
          "<td>" +
          data[i].score["N"] +
          "</td>" +
          "<td>" +
          data[i].player_country["S"] +
          "</td>" +
          "<td>" +
          data[i].player_os["S"] +
          "</td>" +
          "</tr>";
        tableBody.innerHTML += row;
      }
    },
    error: function() {
      console.log("Error occurred during AJAX call.");
    }
  });
}

// Function to update the content of the "Per Country" tab
function updateCountryTab() {
  var tabContent = document.getElementsByClassName("tab-content")[1];

  // Clear the tab content
  tabContent.innerHTML = "";

  // Create subtabs for Brazil, Italy, and Sweden
  var subtabs = ["Brazil", "Italy", "Sweden"];

  // Create subtab buttons
  var subtabButtons = "";
  for (var i = 0; i < subtabs.length; i++) {
    subtabButtons +=
      '<button class="subtab" onclick="changeSubtab(' +
      i +
      ')">' +
      subtabs[i] +
      "</button>";
  }

  // Create subtab content containers
  var subtabContents = "";
  for (var i = 0; i < subtabs.length; i++) {
    subtabContents +=
      '<div id="subtab' +
      i +
      '-content" class="subtab-content"></div>';
  }

  // Append the subtab buttons and contents to the tab content
  tabContent.innerHTML =
    '<div class="subtabs">' +
    subtabButtons +
    "</div>" +
    '<div class="subtab-content-container">' +
    subtabContents +
    "</div>";

  // Set the first subtab as active
  changeSubtab(0);
}

// Function to change the active subtab and show the corresponding content
function changeSubtab(subtabIndex) {
  var subtabButtons = document.getElementsByClassName("subtab");
  var subtabContents = document.getElementsByClassName("subtab-content");

  // Remove "active" class from all subtab buttons and contents
  for (var i = 0; i < subtabButtons.length; i++) {
    subtabButtons[i].classList.remove("active");
    subtabContents[i].style.display = "none";
  }

  // Add "active" class to the selected subtab button and show the corresponding content
  if (subtabIndex !== undefined) {
    subtabButtons[subtabIndex].classList.add("active");
    subtabContents[subtabIndex].style.display = "block";
    updateSubtabData(subtabIndex);
  }
}

// Function to update the data of the active subtab
function updateSubtabData(subtabIndex) {
  var subtabContent = document.getElementById("subtab" + subtabIndex + "-content");

  // Clear the subtab content
  subtabContent.innerHTML = "";
  querystring = "";

  if (subtabIndex == 0) {
    querystring = "?order=player_country&filter=Brazil"
  }
  if (subtabIndex == 1) {
    querystring = "?order=player_country&filter=Italy"
  }
  if (subtabIndex == 2) {
    querystring = "?order=player_country&filter=Sweden"
  }

  // Simulating AJAX call to retrieve updated data for the active subtab
  // Replace this with your actual AJAX call to fetch data from the server
  $.ajax({
    url: API_URL,
    type: "GET",
    headers: {"x-api-key": API_KEY},
    crossDomain: true,
    success: function(data) {

      // Create a table for the subtab content
      var table = document.createElement("table");
      table.classList.add("score-table");
      var tableHead = document.createElement("thead");
      var tableBody = document.createElement("tbody");

      // Create table header
      var headerRow = document.createElement("tr");
      var headers = ["Name", "Points", "Country", "OS"];
      for (var i = 0; i < headers.length; i++) {
        var headerCell = document.createElement("th");
        headerCell.textContent = headers[i];
        headerRow.appendChild(headerCell);
      }
      tableHead.appendChild(headerRow);

      // Create table rows
      for (var i = 0; i < data.length; i++) {
        var row = document.createElement("tr");
        var rowData = [
          data[i].player_name["S"],
          data[i].score["N"],
          data[i].player_country["S"],
          data[i].player_os["S"],
        ];
        for (var j = 0; j < rowData.length; j++) {
          var cell = document.createElement("td");
          cell.textContent = rowData[j];
          row.appendChild(cell);
        }
        tableBody.appendChild(row);
      }

      // Append the table to the subtab content
      table.appendChild(tableHead);
      table.appendChild(tableBody);
      subtabContent.appendChild(table);
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
  if (activeTabIndex === 1) {
    // Per Country tab
    var activeSubtab = document.getElementsByClassName("subtab active")[0];
    var activeSubtabIndex = Array.from(activeSubtab.parentNode.children).indexOf(activeSubtab);
    updateSubtabData(activeSubtabIndex);
  } else {
    updateTableData(activeTabIndex);
  }
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
  if (table.classList.contains("sorted-asc")) {
    rows.reverse();
    table.classList.remove("sorted-asc");
    table.classList.add("sorted-desc");
  } else {
    table.classList.remove("sorted-desc");
    table.classList.add("sorted-asc");
  }

  // Re-append the sorted rows to the table
  tableBody.innerHTML = "";
  for (var i = 0; i < rows.length; i++) {
    tableBody.appendChild(rows[i]);
  }
}
