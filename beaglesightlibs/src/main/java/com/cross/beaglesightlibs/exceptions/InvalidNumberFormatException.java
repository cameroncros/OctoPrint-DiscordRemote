package com.cross.beaglesightlibs.exceptions;

public class InvalidNumberFormatException extends Throwable {
    public InvalidNumberFormatException(NumberFormatException nfe) {
        super(nfe);
    }
}
