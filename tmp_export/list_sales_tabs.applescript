tell application "Google Chrome"
  set out to ""
  set wc to count of windows
  repeat with wi from 1 to wc
    try
      set tc to count of tabs of window wi
      repeat with ti from 1 to tc
        try
          set u to URL of tab ti of window wi
          set n to title of tab ti of window wi
          if u contains "/sales/" then
            set out to out & wi & "," & ti & "," & n & "," & u & linefeed
          end if
        end try
      end repeat
    end try
  end repeat
  return out
end tell
