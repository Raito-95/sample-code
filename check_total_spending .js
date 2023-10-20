var totalUSDAmt = 0; // Total amount in USD
var totalJPYAmt = 0; // Total amount in JPY
var totalTWDAmt = 0; // Total amount in TWD

// Select the parent element containing price information using an appropriate selector
var parentDiv = document.querySelector('#yDmH0d > c-wiz:nth-child(8) > div > div > div:nth-child(4) > div.NgfTBf.fny74c');

if (parentDiv) {
    // Select all div elements with the 'mshXob' class within the specified parent element
    var priceDivs = parentDiv.querySelectorAll('.mshXob');

    // Iterate through all selected elements
    priceDivs.forEach(function(priceDiv) {
        var priceText = priceDiv.textContent; // Get the text content of the element, e.g., US$99.99 or $999.00 or ¥100 or ¥10,000

        // Use regular expression to match different price formats and extract the numeric part
        var match = priceText.match(/(US\$|\$|¥)?([\d,]+(\.\d{2})?|\d+)/);

        if (match) {
            var currencySymbol = match[1] || ''; // Get the currency symbol (if present)
            var priceValue = match[2].replace(/,/g, ''); // Remove commas and convert to a floating-point number

            if (currencySymbol === 'US$') {
                totalUSDAmt += parseFloat(priceValue); // USD
            } else if (currencySymbol === '$') {
                totalTWDAmt += parseFloat(priceValue); // TWD
            } else if (currencySymbol === '¥') {
                totalJPYAmt += parseFloat(priceValue); // JPY
            }
        }
    });

    // Display the total amounts in a single alert
    alert('Total amount in USD: $' + totalUSDAmt.toFixed(2) +
        '\nTotal amount in TWD: TWD ' + totalTWDAmt.toFixed(2) +
        '\nTotal amount in JPY: ¥' + totalJPYAmt.toFixed(2));
}
