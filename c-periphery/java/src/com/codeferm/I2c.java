package com.codeferm;

import com.ochafik.lang.jnaerator.runtime.NativeSize;
import com.sun.jna.Memory;
import com.sun.jna.Pointer;

import peripheryi2c.Peripheryi2cLibrary;
import peripheryi2c.i2c_handle;
import peripheryi2c.i2c_msg;

/**
 * I2C class to handle repetitive operations.
 * 
 * Copyright (c) 2018 Steven P. Goldsmith
 * See LICENSE.md for details.
 */

public class I2c {

	/**
	 * Used for 1 length, so new is not needed each time.
	 */
	private static final NativeSize SIZE1 = new NativeSize(1);
	/**
	 * Used for 2 length, so new is not needed each time.
	 */
	private static final NativeSize SIZE2 = new NativeSize(2);

	// Load JNA library
	final Peripheryi2cLibrary lib = Peripheryi2cLibrary.INSTANCE;

	/**
	 * Get JNA library.
	 * 
	 * @return Library instance.
	 */
	public Peripheryi2cLibrary getLib() {
		return lib;
	}

	/**
	 * Open I2C device and return handle.
	 * 
	 * @param device
	 *            Device path.
	 * @return File handle.
	 */
	public i2c_handle open(final String device) {
		final i2c_handle handle = new i2c_handle();
		if (lib.i2c_open(handle, device) < 0) {
			throw new RuntimeException(lib.i2c_errmsg(handle));
		}
		return handle;
	}

	/**
	 * Close device.
	 * 
	 * @param handle
	 *            I2C file handle.
	 */
	public void close(final i2c_handle handle) {
		if (lib.i2c_close(handle) < 0) {
			throw new RuntimeException(lib.i2c_errmsg(handle));
		}
	}

	/**
	 * Copy from byte array to native memory. For write operations the first byte of
	 * array should contain the register. The second byte indicates the value to
	 * write. Note that for many devices, we can write multiple, sequential
	 * registers at once by simply making buf array bigger.
	 * 
	 * @param addr
	 *            Address.
	 * @param flags
	 *            Flags.
	 * @param buf
	 *            Buffer.
	 * @return Populated i2c_msg.
	 */
	public i2c_msg message(final short addr, final short flags, final byte[] buf) {
		// Reference to the pointer should be kept or it can be garbage collected
		final Pointer bufPtr = new Memory(buf.length);
		// Write byte array to native memory
		bufPtr.write(0, buf, 0, buf.length);
		return new i2c_msg(addr, flags, (short) buf.length, bufPtr);
	}

	/**
	 * Write value to i2c register.
	 * 
	 * @param handle
	 *            I2C file handle.
	 * @param addr
	 *            Address.
	 * @param reg
	 *            Register.
	 * @param value
	 *            Value to write.
	 * @return 0 for no error or error code < 0.
	 */
	public int writeReg(final i2c_handle handle, final short addr, final short reg, final short value) {
		final byte[] data = { (byte) reg, (byte) value };
		return lib.i2c_transfer(handle, message(addr, (short) 0, data), SIZE1);
	}

	/**
	 * Read i2c register.
	 * 
	 * In order to read a register, we first do a "dummy write" by writing 0 bytes
	 * to the register we want to read from. This is similar to writing to a
	 * register except it's 1 byte rather than 2.
	 * 
	 * @param handle
	 *            I2C file handle.
	 * @param addr
	 *            Address.
	 * @param reg
	 *            Register.
	 * @return Register byte value.
	 * 
	 */
	public short readReg(final i2c_handle handle, final short addr, final short reg) {
		final i2c_msg msg = new i2c_msg();
		// Structure.toArray allocates a contiguous block of memory internally
		final i2c_msg[] msgs = (i2c_msg[]) msg.toArray(2);
		// First transaction is write
		final Pointer bufPtr1 = new Memory(1);
		bufPtr1.setByte(0, (byte) reg);
		msgs[0].setAddr(addr);
		msgs[0].setFlags((short) 0);
		msgs[0].setLen((short) 1);
		msgs[0].setBuf(bufPtr1);
		// Second transaction is read
		final Pointer bufPtr2 = new Memory(1);
		// Place holder for data to read
		bufPtr2.setByte(0, (byte) 0x00);
		msgs[1].setAddr(addr);
		msgs[1].setFlags((short) Peripheryi2cLibrary.I2C_M_RD);
		msgs[1].setLen((short) 1);
		msgs[1].setBuf(bufPtr2);
		// Transfer a transaction with two I2C messages
		lib.i2c_transfer(handle, msg, SIZE2);
		return (short) (msgs[1].buf.getByte(0) & 0xff);
	}

	/**
	 * Read two i2c registers and combine them.
	 * 
	 * @param handle
	 *            I2C file handle.
	 * @param addr
	 *            Address.
	 * @param reg
	 *            Register.
	 * @return Register word value.
	 */
	public int readWord(final i2c_handle handle, final short addr, final short reg) {
		final short high = readReg(handle, addr, reg);
		// Increment register for next read
		final short low = readReg(handle, addr, (short) (reg + 1));
		final int value = (high << 8) + low;
		int word = value;
		if (value >= 0x8000) {
			word = -((65535 - value) + 1);
		}
		return word;
	}
}
