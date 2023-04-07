package com.cross.beaglesightlibs.bowconfigs

import java.text.DecimalFormat

abstract class PositionCalculator {
    var positions: List<PositionPair>? = null

    abstract fun calcPosition(distance: Float): Float

    //TODO: Horrifically slow and inaccurate. Replace with optimised version?
    fun getMaxPosition(distStart: Float, distEnd: Float): Float {
        var max = Float.MIN_VALUE
        var i = distStart
        while (i < distEnd) {
            val `val` = calcPosition(i)
            if (`val` > max) {
                max = `val`
            }
            i++
        }
        return max
    }

    //TODO: Horrifically slow and inaccurate. Replace with optimised version?
    fun getMinPosition(distStart: Float, distEnd: Float): Float {
        var min = Float.MAX_VALUE
        var i = distStart
        while (i < distEnd) {
            val `val` = calcPosition(i)
            if (`val` < min) {
                min = `val`
            }
            i++
        }
        return min
    }

    companion object {
        private val zero = DecimalFormat("#")
        private val one = DecimalFormat("#.#")
        private val two = DecimalFormat("#.##")
        fun getDisplayValue(value: Float, numPlaces: Int): String {
            return when (numPlaces) {
                0 -> zero.format(value)
                1 -> one.format(value)
                2 -> two.format(value)
                else -> two.format(value)
            }
        }
    }
}