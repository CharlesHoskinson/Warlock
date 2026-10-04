QPointF QWaylandWindow::mapFromWlSurface(const QPointF &surfacePosition) const
{
    const QMargins margins = clientSideMargins();
    return QPointF(surfacePosition.x() - margins.left(), surfacePosition.y() - margins.top());
}
