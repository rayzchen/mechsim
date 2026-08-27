const canvas = document.getElementById("canvas");
const ctx = canvas.getContext("2d");
ctx.lineCap = "round";

let symbols = {
    names: [],
    latex: []
};
const symbolContainer = document.getElementById("symbol-container");
MathJax.startup = {
    ready() {
        MathJax.startup.defaultReady();
        MathJax.startup.promise.then(() => {
            for (const symbol of symbols.latex) {
                symbolContainer.innerText += "\\(" + symbol + "\\) ";
            }
            MathJax.typesetPromise([symbolContainer]).then(() => {
                const svgs = document.querySelectorAll("#symbol-container svg");
                for (let i = 0; i < svgs.length; i++) {
                    let container = svgs[i].parentElement;
                    symbols[symbols.names[i]] = svgs[i];
                    symbolContainer.appendChild(svgs[i]);
                    container.remove();
                    svgs[i].style.removeProperty("vertical-align");
                }
                symbolContainer.classList.add("shown");
            });
        });
    }
}

function setEquationlabel(label) {
    const equationLabel = document.getElementById("equation-label");
    equationLabel.innerHTML = label;
    MathJax.typesetPromise([equationLabel]).then(() => {
        equationLabel.classList.add("shown");
    });
}

function resetCanvas() {
    ctx.resetTransform();
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.translate(canvas.width / 3, canvas.height / 2);
}

function drawHinge() {
    drawCircle(4, 2);
}

function drawBar(length) {
    ctx.setLineDash([]);
    ctx.beginPath();
    ctx.moveTo(0, 0);
    ctx.lineTo(0, length);
    ctx.lineWidth = 3;
    ctx.stroke();
}

function drawMass() {
    ctx.beginPath();
    ctx.moveTo(0, 0);
    ctx.arc(0, 0, 10, 0, 2 * Math.PI);
    ctx.fillStyle = "black";
    ctx.fill();
}

function drawAxis(length) {
    ctx.setLineDash([2.5, 2.5]);
    ctx.beginPath();
    ctx.moveTo(0, 0);
    ctx.lineTo(0, length);
    ctx.lineWidth = 2;
    ctx.stroke();
}

function drawAngle(angle, radius) {
    angle = (angle + Math.PI) % (2 * Math.PI) - Math.PI;
    if (angle < -Math.PI) {
        angle += 2 * Math.PI;
    }
    ctx.setLineDash([2.5, 2.5]);
    ctx.beginPath();
    ctx.arc(0, 0, radius, angle + Math.PI / 2, Math.PI / 2, angle > 0);
    ctx.lineWidth = 2;
    ctx.stroke();
}

function moveLabel(name, x, y) {
    if (symbols[name] != null) {
        const point = new DOMPoint(x, y);
        const matrix = ctx.getTransform();
        let canvasPoint = matrix.transformPoint(point);
        let x2 = "calc(" + canvasPoint.x + "px - 50%)";
        let y2 = "calc(" + canvasPoint.y + "px - 50%)";
        symbols[name].style.transform = "translate(" + x2 + ", " + y2 + ")";
    }
}

function drawPlane() {
    length = Math.max(canvas.width, canvas.height);
    ctx.setLineDash([]);
    ctx.beginPath();
    ctx.moveTo(-length, 0);
    ctx.lineTo(length, 0);
    ctx.lineWidth = 3;
    ctx.stroke();
}

function drawCircle(radius, width = 3) {
    ctx.setLineDash([]);
    ctx.beginPath();
    ctx.arc(0, 0, radius, 0, 2 * Math.PI);
    ctx.fillStyle = "white";
    ctx.fill();
    ctx.lineWidth = width;
    ctx.stroke();
}

function drawDisk(radius) {
    drawCircle(radius)
    ctx.rotate(-Math.PI / 2);
    drawAxis(radius);
    ctx.rotate(Math.PI / 2);
}

function resize() {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
}
window.addEventListener("load", resize);
window.addEventListener("resize", resize);
