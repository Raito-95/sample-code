// Define variables to store total amounts in different currencies
var totalUSDAmt = 0; // Total amount in US Dollars
var totalJPYAmt = 0; // Total amount in Japanese Yen
var totalTWDAmt = 0; // Total amount in Taiwanese Dollars

// Select the parent element containing price information using an appropriate selector
var parentDiv = document.querySelector("#yDmH0d > c-wiz.SSPGKf.glB9Ve.nI07g > div > div > div:nth-child(4) > div.NgfTBf.fny74c");

if (parentDiv) {
    // Select all div elements with class 'mshXob' within the specified parent element
    var priceDivs = parentDiv.querySelectorAll('.mshXob');

    // Iterate through each selected element
    priceDivs.forEach(function(priceDiv) {
        var priceText = priceDiv.textContent; // Get the text content of the element, e.g., US$99.99 or $999.00 or ¥100 or ¥10,000

        // Use regular expressions to match different price formats and extract the numeric part
        var match = priceText.match(/(US\$|\$|¥)?([\d,]+(\.\d{2})?|\d+)/);

        if (match) {
            var currencySymbol = match[1] || ''; // Get the currency symbol (if present)
            var priceValue = match[2].replace(/,/g, ''); // Remove commas and convert to a floating-point number

            // Add the amount to the corresponding total based on the currency symbol
            if (currencySymbol === 'US$') {
                totalUSDAmt += parseFloat(priceValue); // US Dollars
            } else if (currencySymbol === '$') {
                totalTWDAmt += parseFloat(priceValue); // Taiwanese Dollars
            } else if (currencySymbol === '¥') {
                totalJPYAmt += parseFloat(priceValue); // Japanese Yen
            }
        }
    });

    // Display the total amounts in three different currencies using an alert box
    alert('Total amount in USD: $' + totalUSDAmt.toFixed(2) +
        '\nTotal amount in TWD: TWD ' + totalTWDAmt.toFixed(2) +
        '\nTotal amount in JPY: ¥' + totalJPYAmt.toFixed(2));
}
