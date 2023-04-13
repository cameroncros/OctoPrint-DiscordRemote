package com.cross.beaglesightlibs.bowconfigs

import java.text.DecimalFormat

abstract class BowNumberFormat {
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