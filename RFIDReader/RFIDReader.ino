#include <SPI.h>
#include <MFRC522.h>

#define RST_PIN  9
#define SS_PIN 10
MFRC522 mfrc522(SS_PIN, RST_PIN);

bool rfid_tag_present_prev = false;
bool rfid_tag_present = false;
int rfid_error_counter = 0;
bool tag_found = false;

String detected_tag = "";

void setup()
{
  Serial.begin(9600);
  while (!Serial); // Doesn't hurt to have this. So why not
  SPI.begin();
  mfrc522.PCD_Init();
  Serial.println("Reader has booted");
}

MFRC522::StatusCode detectTag()
{
  // Detect a tag, but ingore collisions. We can get away with it due to the physical design of the prop. There is no way that two tags can fit.
  byte bufferATQA[2];
  byte bufferSize = sizeof(bufferATQA);

  // Reset baud rates
  mfrc522.PCD_WriteRegister(mfrc522.TxModeReg, 0x00);
  mfrc522.PCD_WriteRegister(mfrc522.RxModeReg, 0x00);
  // Reset ModWidthReg
  mfrc522.PCD_WriteRegister(mfrc522.ModWidthReg, 0x26);

  return mfrc522.PICC_RequestA(bufferATQA, &bufferSize);
}

void loop()
{
  rfid_tag_present_prev = rfid_tag_present;

  rfid_error_counter += 1;

  // The counter seems to be flipping back & forth. So we have to use a counter (it always gives false if it's not there, but true and false interlaced if it is there...
  if(rfid_error_counter > 2)
  {
    tag_found = false;
  }

  MFRC522::StatusCode result = detectTag();

  if(result == mfrc522.STATUS_OK)
  {
    if ( ! mfrc522.PICC_ReadCardSerial())
    {
      return;
    }
    rfid_error_counter = 0;
    tag_found = true;
  }

  rfid_tag_present = tag_found;

  // Tag wasn't there but is there now.
  if (rfid_tag_present && !rfid_tag_present_prev)
  {
    Serial.print("Tag found: ");
    detected_tag = toHexString(mfrc522.uid.uidByte, mfrc522.uid.size);
    Serial.println(detected_tag);
  }

  // Tag was there but not anymore.
  if (!rfid_tag_present && rfid_tag_present_prev)
  {
    Serial.print("Tag lost: ");
    Serial.println(detected_tag);
  }
}

String toHexString(byte *buffer, byte bufferSize)
{
  String result = "";
  for (byte i = 0; i < bufferSize; i++)
  {
    result += buffer[i] < 0x10 ? "0" : "";
    result += String(buffer[i], HEX);
  }
  return result;
}
