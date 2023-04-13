package com.cross.beaglesight.composables

import androidx.compose.foundation.Canvas
import androidx.compose.foundation.interaction.MutableInteractionSource
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.geometry.Size
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.PointMode
import androidx.compose.ui.graphics.SolidColor
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.text.*
import androidx.compose.ui.text.font.FontStyle.Companion.Italic
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.cross.beaglesight.ui.theme.BeagleSightTheme
import com.cross.beaglesightlibs.bowconfigs.BowConfig
import com.cross.beaglesightlibs.bowconfigs.PositionPair
import kotlin.math.roundToInt

data class AxisData(
    val start: Offset,
    val end: Offset,
    val label: Offset,
    val text: AnnotatedString
)

@OptIn(ExperimentalTextApi::class)
@Composable
fun SightGraphComposable(
    bowConfig: BowConfig,
    minDist: Float = 0f,
    maxDist: Float = 100f,
    minPos: Float = 0f,
    maxPos: Float = 100f,
    selectedDistanceCallback: (dist: Float, position: Float) -> Unit = { _, _ -> run {} },
    modifier: Modifier,
) {
    var lastBowConfig by remember { mutableStateOf<BowConfig?>(null) }

    val backgroundBrush by remember { mutableStateOf(SolidColor(Color.White)) }
    val lineBrush by remember { mutableStateOf(SolidColor(Color.Red)) }
    val axisBrush by remember { mutableStateOf(SolidColor(Color.Black)) }
    val pointBrush by remember { mutableStateOf(SolidColor(Color.Blue)) }
    val axisFontStyle by remember {
        mutableStateOf(
            SpanStyle(
                color = Color.Black,
                fontSize = 12.sp,
                fontStyle = Italic,
            )
        )
    }

    val textMeasurer = rememberTextMeasurer()
    var touchInteractionState by remember { mutableStateOf<TouchInteraction>(TouchInteraction.NoInteraction) }
    var selectedDistance by remember { mutableStateOf(Float.NaN) }

    val contentWidthStart by remember { mutableStateOf(0.0f) }
    var contentWidthEnd by remember { mutableStateOf(0.0f) }
    val contentHeightStart by remember { mutableStateOf(0.0f) }
    var contentHeightEnd by remember { mutableStateOf(0.0f) }

    val points by remember { mutableStateOf(mutableListOf<Offset>()) }
    val dots by remember { mutableStateOf(mutableListOf<Offset>()) }
    val axis by remember { mutableStateOf(mutableListOf<AxisData>()) }

    fun pixelToDistance(pixel: Float): Float {
        // 20m == contentWidthStart
        // 100m == contentWidthEnd.
        val percent = (pixel - contentWidthStart) / (contentWidthEnd - contentWidthStart)
        return minDist + percent * (maxDist - minDist)
    }

    fun distanceToPixel(distance: Float): Float {
        val percent = (distance - minDist) / (maxDist - minDist)
        return (contentWidthStart + percent * (contentWidthEnd - contentWidthStart)).roundToInt()
            .toFloat()
    }

    fun positionToPixel(position: Float): Float {
        val percent: Float = (position - minPos) / (maxPos - minPos)
        val pixel = contentHeightStart + percent * (contentHeightEnd - contentHeightStart)
        if (pixel.isNaN()) {
            return Float.NaN
        }
        return pixel.roundToInt().toFloat()
    }

    fun calculateYVal(xVal: Float): Float {
        val distance: Float = pixelToDistance(xVal)
        val position: Float =
            bowConfig.calcPosition(distance)
        return positionToPixel(position)
    }

    fun handleTouch(
        touchInteraction: TouchInteraction,
        updateSelectedDistance: (Float) -> Unit,
    ) {
        when (touchInteraction) {
            is TouchInteraction.Move -> {
                val touchPositionX = touchInteraction.position.x
                updateSelectedDistance(pixelToDistance(touchPositionX))
            }

            else -> {
                // nothing to do
            }
        }
    }

    Canvas(modifier = modifier
        .fillMaxSize()
        .touchInteraction(remember { MutableInteractionSource() }) {
            touchInteractionState = it
        }) {
        contentWidthEnd = size.width
        contentHeightEnd = size.height

        if (axis.size == 0) {
            // Calculate x-axis points
            var i = minDist
            while (i < maxDist) {
                val xPixel: Float = distanceToPixel(i)
                if (!xPixel.isNaN()) {
                    axis.add(
                        AxisData(
                            start = Offset(xPixel, contentHeightStart),
                            end = Offset(xPixel, contentHeightEnd),
                            label = Offset(
                                xPixel + 4.dp.toPx(),
                                contentHeightEnd - 12.sp.toPx() - 8.dp.toPx()
                            ),
                            text = buildAnnotatedString {
                                withStyle(style = axisFontStyle) {
                                    append(
                                        "$i"
                                    )
                                }
                            })
                    )
                }
                i += 10f
            }
            // Calculate y-axis points
            i = ((minPos / 10).roundToInt() * 10).toFloat()
            while (i < maxPos) {
                val yPixel: Float = positionToPixel(i)
                if (!yPixel.isNaN()) {
                    axis.add(
                        AxisData(
                            start = Offset(contentWidthStart, yPixel),
                            end = Offset(contentWidthEnd, yPixel),
                            label = Offset(8.dp.toPx(), yPixel),
                            text = buildAnnotatedString {
                                withStyle(style = axisFontStyle) {
                                    append(
                                        "$i"
                                    )
                                }
                            }
                        ))
                }
                i += 10f
            }
        }

        if (lastBowConfig == null || lastBowConfig?.positionArray == bowConfig.positionArray) {
            points.clear()
            dots.clear()

            // Calculate line points
            var xPos = contentWidthStart
            while (xPos < contentWidthEnd) {
                val yVal = calculateYVal(xPos)
                if (!yVal.isNaN()) {
                    points.add(Offset(xPos, yVal))
                }
                xPos += 1f
            }

            // Calculate dots
            for (pair in bowConfig.positionArray) {
                val position: Float = pair.position
                val distance: Float = pair.distance

                val positionPixel = positionToPixel(position)
                val distancePixel = distanceToPixel(distance)

                dots.add(Offset(distancePixel, positionPixel))
            }
            lastBowConfig = bowConfig
        }

        // Draw Background
        drawRect(
            brush = backgroundBrush,
            topLeft = Offset(0f, 0f),
            size = Size(contentWidthEnd, contentHeightEnd)
        )

        // Draw Axis
        for (axisdata in axis) {
            drawLine(
                brush = axisBrush,
                start = axisdata.start,
                end = axisdata.end,
                strokeWidth = 1.dp.toPx()
            )
            drawText(
                textMeasurer = textMeasurer, text = axisdata.text, topLeft = axisdata.label
            )
        }

        // Plot the graph.
        drawPoints(
            points = points,
            pointMode = PointMode.Polygon,
            brush = lineBrush,
            strokeWidth = 2.dp.toPx()
        )

        // Draw the dots.
        for (dot in dots) {
            drawCircle(
                brush = pointBrush,
                radius = 4.dp.toPx(),
                center = dot
            )
        }

        // Draw selected distance
        if (!selectedDistance.isNaN()) {
            val distPx = distanceToPixel(selectedDistance)
            drawLine(
                brush = axisBrush,
                start = Offset(distPx, contentHeightStart),
                end = Offset(distPx, contentHeightEnd),
                strokeWidth = 2.dp.toPx()
            )

            val position = bowConfig.calcPosition(selectedDistance)
            val yPos = positionToPixel(position = position.toFloat())

            drawLine(
                brush = axisBrush,
                start = Offset(contentWidthStart, yPos),
                end = Offset(contentWidthEnd, yPos),
                strokeWidth = 2.dp.toPx()
            )
        }
    }
    handleTouch(
        touchInteractionState,
        updateSelectedDistance = { distance ->
            selectedDistance = distance
            selectedDistanceCallback(
                selectedDistance,
                bowConfig.calcPosition(selectedDistance)
            )
        }
    )
}

@Preview(showBackground = true)
@Composable
fun SightGraphContentPreview() {
    val config = BowConfig()
    config.addPos(PositionPair(10.0f, 10.0f))
    config.addPos(PositionPair(20.0f, 20.0f))
    config.addPos(PositionPair(25.0f, 30.0f))
    config.addPos(PositionPair(30.0f, 40.0f))
    BeagleSightTheme {
        SightGraphComposable(config, modifier = Modifier.testTag("sightgraph"))
    }
}
