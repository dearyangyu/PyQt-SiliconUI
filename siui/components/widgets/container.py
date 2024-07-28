import random
from typing import Union

from PyQt5.Qt import QColor
from PyQt5.QtWidgets import QGraphicsDropShadowEffect

from siui.components.widgets import SiLabel


class ABCDenseContainer(SiLabel):
    """
    密堆容器抽象类
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, *kwargs)

        self.align_center = False  # 是否将所有控件放置在中轴线上
        self.adjust_widgets_size = False  # 子控件适应高度
        self.shrinking = False  # 调整尺寸方法被调用时，允许尺寸变小
        self.use_moveto = False  # 使用 moveto 方法移动控件而非 move

        self.spacing = 16  # 各个控件间的距离

    def setUseMoveTo(self, b: bool):
        """
        在调整控件位置时是否使用 moveto 方法移动控件而非 move
        :param b: 是否使用 moveto
        """
        self.use_moveto = b

    def setAdjustWidgetsSize(self, b: bool):
        """
        设置子控件是否在垂直于容器的方向上自动适应
        :param b: 是否自动适应
        :return:
        """
        self.adjust_widgets_size = b

    def setShrinking(self, b: bool):
        """
        设置调整尺寸方法被调用时，是否尺寸变小
        :param b: 是否允许
        :return:
        """
        self.shrinking = b

    def setAlignCenter(self, b: bool):
        """
        设置是否将子控件放置在容器中轴线上
        :param b: 是否放置在中轴线上
        :return:
        """
        self.align_center = b

    def setSpacing(self, spacing: int):
        """
        设置控件之间的距离
        :param spacing: 距离 px
        :return:
        """
        self.spacing = spacing

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        self.adjustSize()  # 使用 with 语句时，自动调节大小


class SiDenseHContainer(ABCDenseContainer):
    """
    一个可以水平方向紧密靠左或靠右堆叠控件的容器
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, *kwargs)
        self.widgets_left = []
        self.widgets_right = []

    def addPlaceholder(self, length, side="left", index=10000):
        """
        添加占位符
        :param length: 占位符的宽度
        :param side: 添加到哪一侧
        :param index: 插入位置
        :return:
        """
        new_label = SiLabel(self)
        new_label.setVisible(False)
        new_label.resize(length, 0)
        self.addWidget(new_label, side=side, index=index)

    def addWidget(self, widget, side="left", index=10000):
        """
        添加子控件，这将调整被添加的控件的父对象为该容器
        :param widget: 控件
        :param side: 添加到哪一侧
        :param index: 插入位置
        :return:
        """
        widget.setParent(self)

        if side != "left" and side != "right":
            raise ValueError(f"意外方向参数 {side}")

        if side == "left":
            self.widgets_left = self.widgets_left[:index] + [widget] + self.widgets_left[index:]
        if side == "right":
            self.widgets_right = self.widgets_right[:index] + [widget] + self.widgets_right[index:]

        self.adjustSize()

    def getSpareSpace(self):
        """
        获取当前布局条件下，容器剩余的长度或宽度
        :return: 剩余长度或宽度
        """
        # 初始化已使用空间的计数器
        left_used = 0
        right_used = 0

        # 左侧和右侧控件
        for obj in self.widgets_left:
            left_used += obj.width() + self.spacing
        for obj in self.widgets_right:
            right_used += obj.width() + self.spacing

        return self.width() - left_used - right_used

    def removeWidget(self, widget):
        """
        从容器中移除控件
        :param widget: 控件
        """
        if widget in self.widgets_left:
            index = self.widgets_left.index(widget)
            self.widgets_left.pop(index)
            return

        if widget in self.widgets_right:
            index = self.widgets_left.index(widget)
            self.widgets_left.pop(index)
            return

        raise ValueError(f"Widget provided ({widget}) is not in this container.")

    def adjustWidgetsGeometry(self):
        """
        调整子控件的几何信息。这包括排列子控件，置于中轴线上，以及适应容器s
        :return:
        """
        # 初始化已使用空间的计数器
        left_used = 0
        right_used = 0

        # 左侧控件
        for obj in self.widgets_left:
            # 是否适应容器
            if self.adjust_widgets_size is True:
                obj.resize(obj.width(), self.height())

            # 判断并设置是否进行中轴线对齐
            if self.align_center is True:
                y = (self.height() - obj.height()) // 2
            else:
                y = 0

            # 设置位置
            if self.use_moveto is True:
                obj.moveTo(left_used, y)
            else:
                obj.move(left_used, y)

            # 计数器添加控件的宽度和间距
            left_used += obj.width() + self.spacing

        # 右侧控件
        for obj in self.widgets_right:
            # 是否适应容器
            if self.adjust_widgets_size is True:
                obj.resize(obj.width(), self.height())

            # 判断并设置是否进行中轴线对齐
            if self.align_center is True:
                y = (self.height() - obj.height()) // 2
            else:
                y = 0

            # 设置位置
            if self.use_moveto is True:
                obj.moveTo(self.width() - obj.width() - right_used, y)
            else:
                obj.move(self.width() - obj.width() - right_used, y)

            # 计数器添加控件的宽度和间距
            right_used += obj.width() + self.spacing

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.adjustWidgetsGeometry()  # 每当自身尺寸改变时，重新设置控件的位置

    def adjustSize(self):
        """
        根据自身具有的控件调整自身的大小
        :return:
        """
        # 创建计数器
        left_used = 0
        right_used = 0

        # 获取各侧宽度
        for obj in self.widgets_left:
            left_used += obj.width() + self.spacing
        for obj in self.widgets_right:
            right_used += obj.width() + self.spacing

        # 计算总共的宽度，并处理
        total_used = left_used + right_used
        total_used -= 0 if self.widgets_left == [] else self.spacing  # 删去多余的 spacing
        total_used -= 0 if self.widgets_right == [] else self.spacing  # 删去多余的 spacing
        total_used += self.spacing if self.widgets_left + self.widgets_right == [] else 0  # 防止极端情况下两侧控件紧贴
        preferred_w = total_used

        # 计算所有控件中高度最大的，以保证所有控件在容器中
        # preferred_h = max([obj.height() for obj in self.widgets_left + self.widgets_right])

        if self.shrinking is False:
            # 和原本自身的尺寸比价，取最大者
            preferred_w = max(preferred_w, self.width())
            # preferred_h = max(preferred_h, self.height())

        self.resize(preferred_w, self.height())


class SiDenseVContainer(ABCDenseContainer):
    """
    一个可以竖直方向紧密靠上或靠下堆叠控件的容器
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, *kwargs)
        self.widgets_bottom = []
        self.widgets_top = []

    def addPlaceholder(self, length, side="top", index=10000):
        """
        添加占位符
        :param length: 占位符的高
        :param side: 添加到哪一侧
        :param index: 插入位置
        :return:
        """
        new_label = SiLabel(self)
        new_label.setVisible(False)
        new_label.resize(0, length)
        self.addWidget(new_label, side=side, index=index)

    def addWidget(self, widget, side="top", index=10000):
        """
        添加子控件，这将调整被添加的控件的父对象为该容器
        :param widget: 子控件
        :param side: 添加到哪一侧
        :param index: 插入的位置
        :return:
        """
        widget.setParent(self)

        if side != "top" and side != "bottom":
            raise ValueError(f"意外方向参数 {side}")

        if side == "bottom":
            self.widgets_bottom = self.widgets_bottom[:index] + [widget] + self.widgets_bottom[index:]
        if side == "top":
            self.widgets_top = self.widgets_top[:index] + [widget] + self.widgets_top[index:]

        self.adjustSize()

    def getSpareSpace(self):
        """
        获取当前布局条件下，容器剩余的长度或宽度
        :return: 剩余长度或宽度
        """
        # 初始化已使用空间的计数器
        top_used = 0
        bottom_used = 0

        # 左侧和右侧控件
        for obj in self.widgets_top:
            top_used += obj.height() + self.spacing
        for obj in self.widgets_bottom:
            bottom_used += obj.height() + self.spacing

        return self.height() - top_used - bottom_used

    def removeWidget(self, widget):
        """
        从容器中移除控件
        :param widget: 控件
        """
        if widget in self.widgets_top:
            index = self.widgets_top.index(widget)
            self.widgets_top.pop(index)
            return

        if widget in self.widgets_bottom:
            index = self.widgets_bottom.index(widget)
            self.widgets_bottom.pop(index)
            return

        raise ValueError(f"Widget provided ({widget}) is not in this container.")

    def adjustWidgetsGeometry(self):
        """
        调整子控件的几何信息。这包括排列子控件，置于中轴线上，以及适应容器
        :return:
        """
        # 初始化已使用空间的计数器
        top_used = 0
        bottom_used = 0

        # 下侧控件
        for obj in self.widgets_top:
            # 是否适应容器
            if self.adjust_widgets_size is True:
                obj.resize(self.width(), obj.height())

            # 判断并设置是否进行中轴线对齐
            if self.align_center is True:
                x = (self.width() - obj.width()) // 2
            else:
                x = 0

            # 设置位置
            if self.use_moveto is True:
                obj.moveTo(x, top_used)
            else:
                obj.move(x, top_used)

            # 计数器添加控件的宽度和间距
            top_used += obj.height() + self.spacing

        # 上侧控件
        for obj in self.widgets_bottom:
            # 是否适应容器
            if self.adjust_widgets_size is True:
                obj.resize(self.width(), obj.height())

            # 判断并设置是否进行中轴线对齐
            if self.align_center is True:
                x = (self.width() - obj.width()) // 2
            else:
                x = 0

            # 设置位置
            if self.use_moveto is True:
                obj.moveTo(x, self.height() - obj.height() - bottom_used)
            else:
                obj.move(x, self.height() - obj.height() - bottom_used)

            # 计数器添加控件的宽度和间距
            bottom_used += obj.height() + self.spacing

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.adjustWidgetsGeometry()  # 每当自身尺寸改变时，重新设置控件的位置

    def adjustSize(self):
        """
        根据自身具有的控件调整自身的大小
        :return:
        """
        # 创建计数器
        bottom_used = 0
        top_used = 0

        # 获取各侧高度
        for obj in self.widgets_bottom:
            bottom_used += obj.height() + self.spacing
        for obj in self.widgets_top:
            top_used += obj.height() + self.spacing

        # 计算总共的高度，并处理
        total_used = bottom_used + top_used
        total_used -= 0 if self.widgets_bottom == [] else self.spacing  # 删去多余的 spacing
        total_used -= 0 if self.widgets_top == [] else self.spacing  # 删去多余的 spacing
        total_used += self.spacing if (self.widgets_bottom != [] and self.widgets_top != []) else 0  # 防止两侧控件紧贴
        preferred_h = total_used

        # 计算所有控件中宽度最大的，以保证所有控件在容器中
        # preferred_w = max([obj.width() for obj in self.widgets_bottom + self.widgets_top])

        if self.shrinking is False:
            # 和原本自身的尺寸比价，取最大者
            # preferred_w = max(preferred_w, self.width())
            preferred_h = max(preferred_h, self.height())

        self.resize(self.width(), preferred_h)


class SiStackedContainer(SiLabel):
    """
    允许堆叠的容器，可以绑定多个界面，并只显示其中一个
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # 当前索引
        self.current_index_ = -1

        # 所有页面
        self.widgets = []

    def widgetsAmount(self):
        """
        获取子控件的数量
        :return: 子控件数量
        """
        return len(self.widgets)

    def addWidget(self, widget):
        """
        添加子控件（页面）
        :param widget: 子控件
        :return:
        """
        self.insertWidgets(widget, 10000)

    def insertWidgets(self, widget, index: int):
        """
        添加子控件（页面），如果插入位置过大，会置于序列最后
        :param widget: 子控件
        :param index: 索引
        """
        widget.setParent(self)
        widget.resize(self.size())
        widget.move(0, 0)
        widget.hide()
        self.widgets = self.widgets[:index] + [widget] + self.widgets[index:]

        if len(self.widgets) == 1:
            self.setCurrentIndex(0)

    def currentIndex(self):
        """
        获取当前索引
        :return: 索引
        """
        return self.current_index_

    def setCurrentIndex(self, index: int):
        """
        设置当前索引
        :param index: 索引
        """
        self.current_index_ = index
        for widget in self.widgets:
            widget.hide()
        self.widgets[index].show()

    def resizeEvent(self, event):
        super().resizeEvent(event)

        for widget in self.widgets:
            widget.resize(event.size())


class ABCSiFlowContainer(SiLabel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.widgets_ = []
        self.spacing = [8, 8]

    def widgets(self):
        """
        Get the widgets of this container
        :return: widgets
        """
        return self.widgets_

    def addWidget(self, widget, ani=True):
        """
        Add widget to this container
        :param widget: widget
        :param ani: whether to use animation when arranging widgets
        """
        widget.setParent(self)
        self.widgets_.append(widget)
        self.arrangeWidgets(ani=ani)

    def removeWidget(self,
                     widget,
                     has_existence_check: bool = True,
                     delete_later: bool = True):
        """
        Remove a widget in self.widgets()
        :param widget: widget you want to remove
        :param has_existence_check: whether check the existence of the widget in self.widgets()
        :param delete_later: whether run widget.deleteLater()
        """
        if widget in self.widgets_:
            self.widgets_.pop(self.widgets_.index(widget))
            if delete_later:
                widget.deleteLater()
        elif has_existence_check:
            raise ValueError(f"Widget {widget} is not in this container")
        else:
            pass

    def arrangeWidgets(self, ani=True):
        """
        Arrange widgets as its order in self.widgets()
        """
        raise NotImplementedError("arrangeWidgets method must be rewrote.")


class SiFlowContainer(ABCSiFlowContainer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.line_height = 32
        self.preferred_height = 0
        self.dragging_widget = None

    def adjustSize(self):
        self.resize(self.width(), self.preferred_height)

    def regDraggableWidget(self, widget):
        """
        register a widget as a draggable widget
        """
        def on_dragging(pos):
            if self.dragging_widget is None:
                # drop shadow effect
                shadow = QGraphicsDropShadowEffect()
                shadow.setColor(QColor(0, 0, 0, 80))
                shadow.setOffset(0, 0)
                shadow.setBlurRadius(32)
                widget.setGraphicsEffect(shadow)
                self.dragging_widget = widget
            self._on_widget_dragged(widget)

        widget.dragged.connect(on_dragging)

    def _on_widget_dragged(self, dragged_widget):
        self.on_dragging = True
        dragged_widget.raise_()
        center_point = dragged_widget.geometry().center()

        for widget in self.widgets():
            if widget == dragged_widget:
                continue

            if (widget.geometry().contains(center_point) and
                    (widget.getAnimationGroup().fromToken("move").isActive() is False)):

                # insert dragged widget to where this widget is.
                self.insertToByIndex(self.widgets().index(dragged_widget),
                                     self.widgets().index(widget),
                                     no_arrange_exceptions=[dragged_widget])
                break

    def shuffle(self, **kwargs):
        """
        shuffle widgets and rearrange them
        """
        random.shuffle(self.widgets_)
        self.arrangeWidgets(**kwargs)

    def swapByIndex(self, from_index, to_index):
        widget_a = self.widgets()[from_index]
        widget_b = self.widgets()[to_index]
        self.widgets_[from_index] = widget_b
        self.widgets_[to_index] = widget_a
        self.arrangeWidgets()

    def insertToByIndex(self, from_index, to_index, **kwargs):
        widget = self.widgets()[from_index]
        self.widgets_[from_index] = None

        if from_index > to_index:
            self.widgets_ = self.widgets_[:to_index] + [widget] + self.widgets_[to_index:]
        else:
            self.widgets_ = self.widgets_[:to_index+1] + [widget] + self.widgets_[to_index+1:]

        self.widgets_.pop(self.widgets_.index(None))
        self.arrangeWidgets(**kwargs)

    def setLineHeight(self, height, rearrange=True):
        self.line_height = height
        if rearrange:
            self.arrangeWidgets(ani=True)

    def arrangeWidgets(self,
                       ani: bool = True,
                       all_fade_in: bool = False,
                       no_arrange_exceptions: Union[list, None] = None,
                       no_ani_exceptions: Union[list, None] = None):
        """
        :param ani: whether widgets perform animation when arranging them
        :param all_fade_in: let all widgets fade in when arranging them
        :param no_arrange_exceptions: widgets that will not be arranged
        :param no_ani_exceptions: widgets that will not perform moving animation.
        """
        used_width = 0
        used_height = 0
        delay_counter = 0
        if no_arrange_exceptions is None:
            no_arrange_exceptions = []
        if no_ani_exceptions is None:
            no_ani_exceptions = []

        for widget in self.widgets_:
            # warp when haven't got enough space.
            if self.width() - used_width - self.spacing[0] < widget.width():
                used_height += self.spacing[1] + self.line_height
                used_width = 0

            # perform fade in effect
            if all_fade_in or (widget in no_ani_exceptions):
                widget.getAnimationGroup().fromToken("opacity").stop()
                widget.setOpacity(0)
                widget.getAnimationGroup().fromToken("opacity").setTarget(1)
                widget.getAnimationGroup().fromToken("opacity").start(delay=200 + delay_counter)
            delay_counter += 10

            # if we needn't perform animations...
            if (ani is False) or (widget in no_ani_exceptions):
                if (widget in no_arrange_exceptions) is False:
                    widget.getAnimationGroup().fromToken("move").stop()
                    widget.move(used_width + self.spacing[0], used_height)

            # perform animations
            else:
                if (widget in no_arrange_exceptions) is False:
                    widget.moveTo(used_width + self.spacing[0], used_height)

            # add width of this widget to counter
            used_width += widget.width() + self.spacing[0]

        self.preferred_height = used_height + self.spacing[1] + self.line_height

    def resizeEvent(self, event):
        super().resizeEvent(event)
        for widget in self.widgets_:
            widget.setMoveLimits(0, 0, self.width(), self.height())

    def mouseReleaseEvent(self, ev):
        super().mouseReleaseEvent(ev)
        if self.dragging_widget is not None:
            self.dragging_widget.setGraphicsEffect(None)
            self.dragging_widget = None
            self.arrangeWidgets()
