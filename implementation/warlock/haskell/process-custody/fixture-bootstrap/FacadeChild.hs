-- Root-only owned process fixture. It provides no peer authentication.
module Main (main) where
import System.IO (hFlush, hGetLine, stdin, stdout)
main :: IO ()
main = do
 line <- hGetLine stdin
 if line == "finish" then putStrLn "finished" >> hFlush stdout
 else ioError (userError "unexpected fixture input")
