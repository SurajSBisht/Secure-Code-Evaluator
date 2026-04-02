function loadSampleCode() {
  document.getElementById("codeInput").value = `int a = 5;
print(a);
int b = a + 10;`;
}

function analyzeCode() {
  const code = document.getElementById("codeInput").value;

  // Dummy display for now (you already have actual C modules separately)
  document.getElementById("lexicalOutput").textContent =
`Keyword: int
Identifier: a
Operator: =
Number: 5
Delimiter: ;
Keyword: print
Delimiter: (
Identifier: a
Delimiter: )
Delimiter: ;
Keyword: int
Identifier: b
Operator: =
Identifier: a
Operator: +
Number: 10
Delimiter: ;`;

  document.getElementById("syntaxOutput").textContent =
`No syntax errors found.`;

  document.getElementById("semanticOutput").textContent =
`No semantic errors found.`;
}

// Timer Logic
let totalSeconds = 30 * 60;

function updateTimer() {
  const minutes = Math.floor(totalSeconds / 60);
  const seconds = totalSeconds % 60;
  document.getElementById("timer").textContent =
    `Time Left: ${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;

  if (totalSeconds > 0) {
    totalSeconds--;
  } else {
    alert("Time is up! Exam submitted automatically.");
  }
}

setInterval(updateTimer, 1000);

// Fake tab switch warning
document.addEventListener("visibilitychange", function () {
  if (document.hidden) {
    alert("Warning: Tab switching detected!");
  }
});