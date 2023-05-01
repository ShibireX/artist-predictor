document.addEventListener('DOMContentLoaded', function() {
    const rangeInput = document.getElementById('popularity-range');
    const rangeLabel = document.getElementById('popularity-label');
    const hiddenInput = document.getElementById("popularity-value");
  
    rangeInput.addEventListener('input', function() {
        const currentValue = rangeInput.value;
        rangeLabel.innerText = Math.round(Math.pow(10, currentValue));
        hiddenInput.value = parseInt(rangeLabel.innerText);
    });
  });