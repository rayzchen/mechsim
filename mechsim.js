const canvas = document.getElementById("canvas");
const ctx = canvas.getContext("2d");
ctx.lineCap = "round";

let symbols = {};
const symbolContainer = document.getElementById("symbols");
const observer = new MutationObserver((list, observer) => {
    console.log("observed");
    const names = ["t1", "l1", "m1", "t2", "l2", "m2"];
    const svgs = document.querySelectorAll("#symbols svg");
    console.log(svgs);
    if (svgs.length != names.length) return;

    observer.disconnect();
    for (let i = 0; i < svgs.length; i++) {
        let container = svgs[i].parentElement;
        symbols[names[i]] = svgs[i];
        symbolContainer.appendChild(svgs[i]);
        container.remove();
        svgs[i].style.removeProperty("vertical-align");
    }
});
observer.observe(symbolContainer, {childList: true, subtree: true});

function setEquationlabel(label) {
    const equationLabel = document.getElementById("equation-label");
    equationLabel.innerHTML = label;
    MathJax.typesetPromise([equationLabel]).then(() => {
        equationLabel.style.display = "block";
    });
}

function drawHinge() {
    ctx.setLineDash([]);
    ctx.beginPath();
    ctx.arc(0, 0, 3, 0, 2 * Math.PI);
    ctx.lineWidth = 4;
    ctx.stroke();
    ctx.fillStyle = "white";
    ctx.fill();
}

function drawBar() {
    ctx.setLineDash([]);
    ctx.beginPath();
    ctx.moveTo(0, 0);
    ctx.lineTo(0, 100);
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

function drawAxis() {
    ctx.setLineDash([2.5, 2.5]);
    ctx.beginPath();
    ctx.moveTo(0, 0);
    ctx.lineTo(0, 50);
    ctx.lineWidth = 2;
    ctx.stroke();
}

function drawAngle(angle) {
    angle = (angle + Math.PI) % (2 * Math.PI) - Math.PI;
    if (angle < -Math.PI) {
        angle += 2 * Math.PI;
    }
    let start, end;
    if (angle < 0) {
        start = angle + Math.PI / 2;
        end = Math.PI / 2;
    } else {
        start = Math.PI / 2;
        end = angle + Math.PI / 2;
    }
    ctx.setLineDash([2.5, 2.5]);
    ctx.beginPath();
    ctx.arc(0, 0, 35, start, end);
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
        symbolContainer.style.display = "block";
    }
}

function resize() {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
}
window.addEventListener("load", resize);
window.addEventListener("resize", resize);
