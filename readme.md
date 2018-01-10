# Команды

## PoiAlign

Аргументы: точки-POI (хотя бы одна), линии-соединители POI со зданием и линия-здание (обязательно).
Зданием будет считаться линия без `highway`.

* Ставит POI на расстояние 2 метров от стены здания.
* Если POI соединена со зданием одной из указанных линий-соединителей так, что в линии-соединителе между POI и зданием нет других точек, сдвигает POI так, что отрезок соединителя образует биссектрису угла, образуемого стенами здания в точке соединения. Проще говоря, если стена здания в точке соединения не кривая, соединяющий отрезок встанет к ней перпендикулярно.
* Если на точке стоял `entrance`, убирает с неё `entrance`, ставит `entrance` на стену здания и соединяет получившийся вход с POI с помощью `highway=corridor`.
