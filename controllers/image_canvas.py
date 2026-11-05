from math import ceil, floor
from PyQt6.QtCore import Qt, QPointF, QRectF, QLineF, pyqtSignal
from PyQt6.QtGui import QPainter, QColor, QPen
from PyQt6.QtWidgets import QAbstractScrollArea

K = Qt.Key
KEYS = {K.Key_Left: (-1, 0), K.Key_Comma: (-1, 0), K.Key_Less: (-1, 0),
        K.Key_Right: (1, 0), K.Key_Period: (1, 0), K.Key_Greater: (1, 0),
        K.Key_Up: (0, -1), K.Key_Down: (0, 1)}


class ImageCanvas(QAbstractScrollArea):
    selected = pyqtSignal(int, int)  # mcu x, y

    def __init__(s):
        super().__init__()
        s.pm = None; s.mw = s.mh = 0
        s.z, s.o, s.sel = 1.0, QPointF(), (0, 0)
        s._auto = True; s._moved = False; s._last = QPointF()
        s.setMinimumSize(400, 300)
        s.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        s.viewport().setCursor(Qt.CursorShape.CrossCursor)
        # luôn bật để viewport không đổi kích thước khi zoom (tránh vòng lặp resize)
        s.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        s.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        s.horizontalScrollBar().valueChanged.connect(s._scroll)
        s.verticalScrollBar().valueChanged.connect(s._scroll)

    # ---- state ----
    def set_pixmap(s, pm, mcu=None):
        if s.pm is None or pm.size() != s.pm.size(): s._auto = True  # ảnh mới -> fit; View lại giữ zoom/pan
        s.pm, (s.mw, s.mh) = pm, mcu or (0, 0)
        s.fit() if s._auto else s._layout()

    def clear(s): s.pm = None; s._layout()

    def set_sel(s, x, y): s.sel = (x, y); s._reveal()

    def _layout(s):
        """Clamp offset (ảnh nhỏ hơn viewport thì canh giữa) + đồng bộ scrollbar."""
        v = s.viewport()
        W, H = (s.pm.width() * s.z, s.pm.height() * s.z) if s.pm else (0, 0)
        ax = lambda o, sz, vs: (vs - sz) / 2 if sz <= vs else min(0, max(vs - sz, o))
        s.o = QPointF(ax(s.o.x(), W, v.width()), ax(s.o.y(), H, v.height()))
        for bar, sz, vs, o in ((s.horizontalScrollBar(), W, v.width(), s.o.x()),
                               (s.verticalScrollBar(), H, v.height(), s.o.y())):
            big = sz > vs
            bar.blockSignals(True)
            bar.setRange(0, ceil(sz - vs) if big else 0)
            bar.setPageStep(vs); bar.setSingleStep(max(1, vs // 10))
            bar.setValue(round(-o) if big else 0)
            bar.blockSignals(False)
        v.update()

    def _scroll(s, _):
        s._auto = False
        h, w = s.horizontalScrollBar(), s.verticalScrollBar()
        s.o = QPointF(-h.value() if h.maximum() else s.o.x(), -w.value() if w.maximum() else s.o.y())
        s.viewport().update()

    def fit(s):
        if not s.pm: return
        v = s.viewport()
        s._auto, s.z, s.o = True, min(v.width() / s.pm.width(), v.height() / s.pm.height()), QPointF()
        s._layout()

    def zoom(s, f, c=None):  # chỉ đổi z/o, không đụng s.sel
        if not s.pm: return
        s._auto = False
        v = s.viewport()
        c = c or QPointF(v.width() / 2, v.height() / 2)
        z = min(max(s.z * f, 0.02), 64); f = z / s.z
        s.o, s.z = c - (c - s.o) * f, z
        s._layout()

    def _reveal(s):
        """Cuộn để MCU đang chọn nằm trong viewport."""
        if not (s.pm and s.mw): return
        v, z, (sx, sy) = s.viewport(), s.z, s.sel
        d = []
        for p, c, vs in ((s.o.x() + sx * s.mw * z, s.mw * z, v.width()), (s.o.y() + sy * s.mh * z, s.mh * z, v.height())):
            d.append(-p if p < 0 or c > vs else min(0, vs - (p + c)))
        if d[0] or d[1]: s._auto = False; s.o += QPointF(*d)
        s._layout()

    def _step(s, dx, dy):
        if not (s.pm and s.mw): return
        cols, rows = ceil(s.pm.width() / s.mw), ceil(s.pm.height() / s.mh)
        s.sel = (min(max(s.sel[0] + dx, 0), cols - 1), min(max(s.sel[1] + dy, 0), rows - 1))
        s.selected.emit(*s.sel); s._reveal()

    # ---- events ----
    def resizeEvent(s, e):
        super().resizeEvent(e)
        s.fit() if s._auto else s._layout()

    def enterEvent(s, e): s.setFocus()  # hover là dùng được phím điều hướng

    def keyPressEvent(s, e):
        if (d := KEYS.get(e.key())): s._step(*d)
        else: super().keyPressEvent(e)

    def wheelEvent(s, e): s.zoom(1.25 ** (e.angleDelta().y() / 120), e.position())

    def mousePressEvent(s, e):
        s._last, s._moved = e.position(), False

    def mouseMoveEvent(s, e):
        if not e.buttons() & Qt.MouseButton.LeftButton: return
        p = e.position()
        if not s._moved and (p - s._last).manhattanLength() < 4: return
        s._moved, s._auto = True, False
        s.o += p - s._last; s._last = p; s._layout()

    def mouseReleaseEvent(s, e):
        if s._moved or not (s.pm and s.mw): return
        p = (e.position() - s.o) / s.z
        if 0 <= p.x() < s.pm.width() and 0 <= p.y() < s.pm.height():
            s.sel = (int(p.x() // s.mw), int(p.y() // s.mh))
            s.selected.emit(*s.sel); s.viewport().update()

    def paintEvent(s, e):
        if not s.pm: return
        v = s.viewport(); vw, vh = v.width(), v.height()
        p, z, o = QPainter(v), s.z, s.o
        p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, z < 1)
        p.translate(o); p.scale(z, z); p.drawPixmap(0, 0, s.pm); p.resetTransform()
        if not s.mw: return
        W, H, cw, ch = s.pm.width() * z, s.pm.height() * z, s.mw * z, s.mh * z
        if min(cw, ch) >= 4:  # quá dày thì bỏ lưới
            y0, y1, x0, x1 = max(o.y(), 0), min(o.y() + H, vh), max(o.x(), 0), min(o.x() + W, vw)
            xs = range(max(0, floor(-o.x() / cw)), ceil(min(W, vw - o.x()) / cw) + 1)
            ys = range(max(0, floor(-o.y() / ch)), ceil(min(H, vh - o.y()) / ch) + 1)
            p.setPen(QPen(QColor(0, 255, 255, 150)))
            p.drawLines([QLineF(o.x() + min(i * cw, W), y0, o.x() + min(i * cw, W), y1) for i in xs] +
                        [QLineF(x0, o.y() + min(j * ch, H), x1, o.y() + min(j * ch, H)) for j in ys])
        sx, sy = s.sel
        p.setPen(QPen(QColor(255, 0, 0), 2)); p.setBrush(QColor(255, 0, 0, 60))
        p.drawRect(QRectF(o.x() + sx * cw, o.y() + sy * ch, cw, ch))
