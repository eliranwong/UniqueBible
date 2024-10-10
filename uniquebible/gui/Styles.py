from uniquebible import config


# Examples: https://doc.qt.io/qt-5/stylesheet-examples.html

def defineStyle():

    if config.menuLayout == "material" and config.qtMaterial:
        config.theme = "dark" if config.qtMaterialTheme.startswith("dark_") else "default"
        config.qtMaterial = False

    config.widgetStyle = """QWidget {0}
    border: 0px;
    border-radius: 0px;
    padding: 0 0px;
    background-color: {2}; color: {3};{1} QWidget:hover {0}background-color: {4}; color: {5};{1} QWidget:pressed {0}background-color: {6}; color: {7}
    {1}""".format("{", "}", config.widgetBackgroundColor, config.widgetForegroundColor, config.widgetBackgroundColorHover, config.widgetForegroundColorHover, config.widgetBackgroundColorPressed, config.widgetForegroundColorPressed)

    config.materialStyle = """

QLabel {0} font-size: {9}px; color: {3}; {1}

QToolTip {0}
    font-size: {9}px;
    background-color: {4};
    color: {5};
    border: 2px solid {2};
    padding: 5px;
    border-radius: 3px;
    opacity: 200;
{1}

QToolBar {0} font-size: {9}px; icon-size: {8}px; {1}

QPushButton {0} font-size: {9}px; icon-size: {8}px; background-color: {2}; color: {3};{1} QPushButton:hover {0}background-color: {4}; color: {5};{1} QPushButton:pressed {0}background-color: {6}; color: {7}{1} QPushButton:checked {0}background-color: {6}; color: {7}{1}

QToolButton {0} /* all types of tool button */
    font-size: {9}px;
    background-color: {2};
    color: {3};
{1}

QToolButton:hover {0}
    background-color: {4};
    color: {5};
{1}

QToolButton:pressed {0}
    background-color: {6};
    color: {7};
{1}

QToolButton::menu-button {0}
    border: 2px solid gray;
    border-top-right-radius: 6px;
    border-bottom-right-radius: 6px;
    /* 16px width + 4px for border = 20px allocated above */
    width: 150px;
{1}

QComboBox {0} font-size: {9}px; background-color: {2}; color: {3}; {1}
QComboBox:hover {0} background-color: {4}; color: {5}; {1}
/* selection-background-color in QAbstractItemView does not work if QComboBox has an assigned background-color
QComboBox QAbstractItemView {0} background-color: {2}; color: {3}; {1}
Therefore, we use QComboBox::item instead of QComboBox QAbstractItemView.
*/
QComboBox::item {0} background-color: {2}; color: {3}; {1}
QComboBox::item:selected {0} border: solid {3}; background-color: {3}; color: {2}; {1}

/* For checkbox in QComboBox */
QAbstractItemView::indicator {0} background-color: {2}; {1}
QAbstractItemView::indicator:checked {0} background-color: {3}; {1}

QRadioButton {0} font-size: {9}px; background-color: {2}; color: {3}; {1}
QRadioButton:hover {0} background-color: {4}; color: {5}; {1}
QRadioButton:checked {0} background-color: {6}; color: {7}; {1}

QCheckBox {0} font-size: {9}px; background-color: {2}; color: {3}; {1}
QCheckBox:hover {0} background-color: {4}; color: {5}; {1}
QCheckBox:checked {0} background-color: {6}; color: {7}; {1}

QLineEdit {0}
    font-size: {9}px;
    border: 2px solid {4};
    border-radius: 10px;
    padding: 0 8px;
    background: {2};
    color: {3};
    selection-background-color: {3};
    selection-color: {2};
{1}

QTextEdit {0}
    selection-background-color: {4};
    selection-color: {5};
{1}

QListView {0}
    font-size: {9}px;
    selection-background-color: {4};
    selection-color: {5};
{1}

QListView::item:hover {0}
    font-size: {9}px;
    background-color: {5};
    color: {4};
{1}

QPlainTextEdit {0}
    font-size: {12}px;
    selection-background-color: {4};
    selection-color: {5};
{1}

QTableView {0}
    font-size: {9}px;
    selection-background-color: {4};
    selection-color: {5};
{1}

QHeaderView::section {0}
    font-size: {9}px;
    background-color: {2};
    color: {3};
{1}

/* Style the tab using the tab sub-control. Note that
    it reads QTabBar _not_ QTabWidget */
QTabWidget::tab-bar {0}
    left: 2px; /* move to the right by 2px */
{1}

QTabBar::tab {0}
    font-size: {9}px;
    background-color: {2};
    color: {3};
    border: 2px solid {2};
    border-bottom-color: {3};
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
    min-width: {11}px;
    min-height: {9}px;
    padding: 4px;
{1}

QTabBar::tab:hover {0}
    background-color: {4};
    color: {5};
    border: 2px solid {4};
    border-bottom-color: {5};
{1}

QTabBar::tab:selected {0}
    background-color: {6};
    color: {7};
    border-color: {7};
    border-bottom-color: {6};
{1}

QTabBar::tab:!selected {0}
    margin-top: 2px; /* make non-selected tabs look smaller */
{1}

QMenu {0}
    font-size: {9}px;
    background-color: {2}; /* sets background of the menu */
    color: {3};
    border: 1px solid {4};
{1}

QMenu::item {0}
    /* sets background of menu item. set this to something non-transparent
        if you want menu color and menu item color to be different */
    background-color: transparent;
{1}

QMenu::item:selected {0} /* when user selects item using mouse or keyboard */
    background-color: {3};
    color: {2};
{1}

QMenu::separator {0}
    background: {4};
{1}

QMenuBar {0}
    font-size: {9}px;
    background-color: {2};
    color: {3};
    spacing: 3px; /* spacing between menu bar items */
{1}

QMenuBar::item {0}
    padding: 1px 4px;
    background: transparent;
    border-radius: 4px;
{1}

QMenuBar::item:selected {0} /* when selected using mouse or keyboard */
    background: {4};
    color: {5};
{1}

QMenuBar::item:pressed {0}
    background: {6};
    color: {7};
{1}

QProgressBar {0}
    border: 2px solid {4};
    border-radius: 5px;
    text-align: center;
{1}

QProgressBar::chunk {0}
    background-color: {7};
    color: {6};
    width: 20px;
{1}

QSplitter::handle {0}
    background-color: {2};
{1}

QSplitter::handle:hover {0}
    background-color: {4};
{1}

QSplitter::handle:pressed {0}
    background-color: {6};
{1}

QGroupBox::title {0}
    font-size: {9}px;
    color: {3};
{1}

QSlider::handle {0}
    background-color: {7};
    border: 1px solid {6};
    border-radius: 3px;
{1}

QSlider::add-page {0}
    background-color: {4};
{1}

QSlider::sub-page {0}
    background-color: {3};
{1}

    """.format(
        "{",
        "}",
        config.widgetBackgroundColor,
        config.widgetForegroundColor,
        config.widgetBackgroundColorHover,
        config.widgetForegroundColorHover,
        config.widgetBackgroundColorPressed,
        config.widgetForegroundColorPressed,
        config.iconButtonSize,
        (int(config.iconButtonSize * 2/3)),
        (int(config.iconButtonSize / 2)),
        (int(config.iconButtonSize * 5)),
        (int(config.iconButtonSize * 2/3)+5),
        )

# Get a color variant
# Source of the following method: https://chase-seibert.github.io/blog/2011/07/29/python-calculate-lighterdarker-rgb-colors.html
def getColorVariant(hex_color, brightness_offset=1):
    """ takes a color like #87c95f and produces a lighter or darker variant """
    if len(hex_color) != 7:
        raise Exception("Passed {0} into color_variant(), needs to be in #87c95f format.".format(hex_color))
    rgb_hex = [hex_color[x:x+2] for x in [1, 3, 5]]
    new_rgb_int = [int(hex_value, 16) + brightness_offset for hex_value in rgb_hex]
    new_rgb_int = [min([255, max([0, i])]) for i in new_rgb_int] # make sure new values are between 0 and 255
    # hex() produces "0x88", we want just "88"
    return "#" + "".join([hex(i)[2:] for i in new_rgb_int])


config.defineStyle = defineStyle
#config.getColorVariant = getColorVariant