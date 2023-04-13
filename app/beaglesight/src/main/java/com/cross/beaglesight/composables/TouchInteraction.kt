package com.cross.beaglesight.composables

import androidx.compose.foundation.gestures.forEachGesture
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.input.pointer.PointerEvent
import androidx.compose.ui.input.pointer.pointerInput


sealed class TouchInteraction {
    object NoInteraction : TouchInteraction()
    data class Move(val position: Offset) : TouchInteraction()
}

fun Modifier.touchInteraction(key: Any, block: (TouchInteraction) -> Unit): Modifier =
    pointerInput(key) {
        forEachGesture {
            awaitPointerEventScope {
                do {
                    val event: PointerEvent = awaitPointerEvent()

                    block(TouchInteraction.Move(event.changes.first().position))
                } while (event.changes.any { it.pressed })
            }
        }
    }