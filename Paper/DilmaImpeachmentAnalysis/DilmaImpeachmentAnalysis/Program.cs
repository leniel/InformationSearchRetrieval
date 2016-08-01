using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using iTextSharp.text.pdf;
using iTextSharp.text.pdf.parser;
using System.IO;
using NPOI.SS.UserModel;
using NPOI.XSSF.UserModel;
using System.Globalization;
using System.Text.RegularExpressions;

namespace DilmaImpeachmentAnalysis
{
    class Program
    {
        static void Main(string[] args)
        {
            var pdfText = ExtractTextFromPdf(@"Y:\Dev\InformationSearchRetrieval\Paper\EV1704161400.pdf");

            var votes = ParseVotes(pdfText);

            WriteVotesToExcel(votes);
        }

        /// <summary>
        /// Extracts the PDF full text.
        /// </summary>
        /// <param name="path">Path to PDF file</param>
        /// <returns></returns>
        private static string ExtractTextFromPdf(string path)
        {
            using(PdfReader reader = new PdfReader(path))
            {
                StringBuilder text = new StringBuilder();

                // Voting transcription starts at page 121 and ends at page 323
                for(int i = 121; i <= 323; i++)
                {
                    text.Append(PdfTextExtractor.GetTextFromPage(reader, i));
                }

                return text.ToString();
            }
        }

        /// <summary>
        /// Parses the full PDF text to extract the relavent info that contains deputies' names, party, state and speech.
        /// </summary>
        /// <param name="text">PDF full text</param>
        /// <returns></returns>
        private static List<Vote> ParseVotes(string text)
        {
            var votes = new List<Vote>();

            var sentences = text.Split(new[] { "O SR.", "A SRA." }, StringSplitOptions.None).AsEnumerable();

            // Removing white space...
            sentences = sentences.Select(s => s.TrimStart());

            // Filtering to keep only the Deputies' votes...
            var filtered = sentences.Where(s => !s.StartsWith("PRESIDENTE") && !s.StartsWith("BETO MANSUR") && !s.StartsWith("FELIPE BORNIER") && !s.StartsWith("ALEX CANZIANI") && !s.StartsWith("CÂMARA DOS DEPUTADOS"));

            // Removes page number followed by header text present in every page with session number, etc.
            // Single line changes how the .dot operator works: http://stackoverflow.com/a/1780037/114029
            var regex = new Regex(@"\d+(.*)4176", RegexOptions.Singleline);

            foreach(var s in filtered)
            {
                var parts = s.Split(new[] { " - " }, StringSplitOptions.None);

                if(parts.Length > 2)
                {
                    for(int i = 2; i < parts.Length; i++)
                    {
                        parts[1] += parts[i];
                    }
                }

                var deputy = parts.ElementAt(0);

                var deputyParts = deputy.Split(new[] { '(', ')' }, StringSplitOptions.RemoveEmptyEntries);

                deputy = CultureInfo.CurrentCulture.TextInfo.ToTitleCase(deputyParts[0].ToLower()).TrimEnd();

                var party = deputyParts.Length > 1 ? deputyParts[1].TrimEnd('.') : string.Empty;

                var partyParts = party.Split('-');

                // Removing the word "Bloco/"
                party = partyParts[0].Replace("Bloco/", string.Empty);

                var state = partyParts.Length > 1 ? partyParts[1].Substring(0, 2) : string.Empty;

                var speech = parts.ElementAt(1);

                speech = regex.Replace(speech, string.Empty);

                var vote = new Vote { Deputy = deputy, Party = party, State = state, Speech = speech };

                TreatExceptionInData(vote);

                if(!votes.Any(v => v.Deputy == vote.Deputy))
                {
                    votes.Add(vote);
                }
                else
                {
                    var deputyVote = votes.Single(v => v.Deputy == vote.Deputy);

                    if(deputyVote.State == string.Empty)
                    {
                        deputyVote.State = vote.State;
                        deputyVote.Party = vote.Party;
                    }

                    // Append the speech continuation for that deputy...
                    deputyVote.Speech += vote.Speech;
                }
            }

            return votes;
        }

        private static void TreatExceptionInData(Vote vote)
        {
            if(vote.Deputy == "Pr. Marco Feliciano")
            {
                vote.State = "SP";

                return;
            }

            if(vote.State == "Mi")
            {
                vote.State = "MG";

                return;
            }
        }

        /// <summary>
        /// Writes voting info to an Excel file.
        /// </summary>
        /// <param name="votes">List of Votes</param>
        private static void WriteVotesToExcel(List<Vote> votes)
        {
            // Writing the voting data to an Excel file...
            IWorkbook workbook = new XSSFWorkbook();
            ISheet sheet = workbook.CreateSheet("Votes");

            IRow row = sheet.CreateRow(0);

            // Columns' headers
            row.CreateCell(1).SetCellValue("Deputy");
            row.CreateCell(2).SetCellValue("Party");
            row.CreateCell(3).SetCellValue("State");
            row.CreateCell(4).SetCellValue("Speech");

            for(int i = 0; i < votes.Count; i++)
            {
                var vote = votes[i];

                row = sheet.CreateRow(i + 1);

                row.CreateCell(1).SetCellValue(vote.Deputy);
                row.CreateCell(2).SetCellValue(vote.Party);
                row.CreateCell(3).SetCellValue(vote.State);
                row.CreateCell(4).SetCellValue(vote.Speech);
            }

            FileStream fs = File.Create("Dilma's Impeachment Votes.xlsx");

            workbook.Write(fs);

            fs.Close();
        }
    }
}
